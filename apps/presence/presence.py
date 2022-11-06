import appdaemon.plugins.hass.hassapi as hass

class Presence(hass.Hass):

    def initialize(self):
        self.output_map = {}
        self.debug = self.args["debug"] if "debug" in self.args else False
        for sensor in self.args["sensors"]:
            self.logd("sensor", sensor)
            input = sensor["input"]
            output = sensor["output"]
            self.output_map[input] = output
            self.listen_state(self.motion_state_updated, input)
        for tracker in self.get_trackers():
            self.logd("tracker", tracker)
            self.listen_state(self.presence_updated, tracker)
        self.default = self.args["default_location"]
        self.fallback_location = None
        self.last_detected = None
        self.home = False
        self.presence_updated(None, None, None, None, None)
        self.currently_detecting = set()
        
    def set(self, sensor, state):
        self.set_state(self.output_map[sensor], state = state)
    
    def update_motion(self, entity):
        self.currently_detecting.add(entity)
        self.last_detected = entity
        if self.fallback_location:
            self.logd("motion detected, no longer has fallback location", str(self.fallback_location))
            if not self.fallback_location == entity:
                self.set(self.fallback_location, "off")
            self.fallback_location = None
        self.set(entity, "on")
        
    
    def update_no_motion(self, entity):
        self.currently_detecting.remove(entity)
        if len(self.currently_detecting) == 1:
            self.last_detected = self.currently_detecting.pop()
            self.currently_detecting.add(self.last_detected)
        if self.home and not self.fallback_location and self.last_detected == entity:
            self.logd("no motion detected, entering fallback location state", str(entity))
            self.fallback_location = entity
        if not self.fallback_location == entity:
            self.set(entity, "off")

    def motion_state_updated(self, entity, attribute, old, new, kwargs):
        self.logd("--motion state--")
        self.log_args(entity, attribute, old, new, kwargs)
        
        if ("state" in new and new["state"] == "on" and old["state"] == "off") or new == "on":
            self.update_motion(entity)
        else:
            self.update_no_motion(entity)

    def presence_updated(self, entity, attribute, old, new, kwargs):
        self.logd("--presence state--")
        self.log_args(entity, attribute, old, new, kwargs)
        
        if not self.anyone_home() and self.fallback_location:
            self.logd("nobody home, turning off fallback location", str(self.fallback_location))
            self.set(self.fallback, "off")
            self.fallback_location = None
            self.home = False
        elif self.anyone_home() and not self.home:
            self.logd("somebody got home, turning on default location", str(self.fallback_location), str(entity), str(self.default))
            self.fallback_location = self.default
            self.set(self.fallback_location, "on")
        self.home = self.anyone_home()
    
    def log_args(self, entity, attribute, old, new, kwargs):
        self.logd("entity", entity)
        self.logd("attribute", attribute)
        self.logd("old", old)
        self.logd("new", new)
        self.logd("kwargs", kwargs)
    
    def logd(self, *args):
        if self.debug:
            self.log(" | ".join([arg if isinstance(arg, str) else repr(arg) for arg in args]))