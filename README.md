<div align="center">
# Presence for Home Assistant
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
</div>

This is a small AppDaemon app for handling things in related to motion sensors in Home Assistant that are tricky to handle with normal Automations. Currently that means making sure that there is always (at least) one sensor signalling presence whenever someone is home.
This gets rid of the problem when you e.g. sit very still and read a book, or are simply in a section of the room with poor motion sensor coverage; as long as any individual has their location set to `home` (through GPS sensor, wifi detection etc.) the last detected motion sensor will remain on, even if the physical sensor is not detecting any motion.

## Example config
In apps.yaml:
```
room_presence:
  module: presence
  class: Presence
  sensors:
    - input: binary_sensor.motion_sensor1
      output: input_boolean.motion_sensor1_output
    - input: binary_sensor.motion_sensor2
      output: input_boolean.motion_sensor2_output
    - input: binary_sensor.motion_sensor2
      output: input_boolean.motion_sensor3_output
  default_location: binary_sensor.motion_sensor2
```

Here `binary_sensor.motion_sensor[1-3]` are your actual motion sensor entities, while the outputs are Helpers that you have created and are used as the inputs for your Automations.
The `default_location` is the location that turns on if somebody's location is set to `home` before any motion sensors have been triggered. I suggest you use the sensor nearest the entrance as your default location.

## Scope
There are many configurations of motion sensors that this application cannot, and will not, handle on its own, simply because it can be trivially done in HA already:
 - If you want to add debouncing to your outputs that can be done in your Automations by putting a lower limit on the time the motion state has to be off before triggering.
 - If you want to combine multiple sensors to cover a large room you can create a Group in HA and use that as the input to Presence. Whenever any motion sensor in a Group detects movement the Group itself will also signal movement.
 - Any binary sensor works, so you can also combine motion sensors with magnetic door sensors in the same group.

## Installing
In HACS, click Automation and then the three dots in the upper right corner. Click Custom repositories and paste the URL of this repo in the Repository field. For the Category field, select AppDaemon.
