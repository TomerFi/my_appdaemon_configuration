# My AppDaemon Configuration</br>[![maintained]][0] [![appd-version]][1] [![appd-environment]][2] [![hardware]][3]

This is my [AppDaemon](https://appdaemon.readthedocs.io/en/latest/index.html) configuration.

You can also check out my [Home Assistant][4] configuration and my [Docker][5] configuration.

Please note, *AppDaemon* original docker image is not suitable for running on *rpi3b*.

To make it work I'm actually running a local image which I tweaked a little bit by
changing the base image to [arm32v7/python:3.6-alpine](https://hub.docker.com/r/arm32v7/python).

<!-- real links -->
[0]: https://github.com/TomerFi/my_appdaemon_configuration
[1]: https://github.com/home-assistant/appdaemon/releases/tag/3.0.5
[2]: https://appdaemon.readthedocs.io/en/latest/INSTALL.html#install-and-run-using-docker
[3]: https://www.raspberrypi.org/products/raspberry-pi-3-model-b/
[4]: https://github.com/TomerFi/my_home_assistant_configuration
[5]: https://github.com/TomerFi/my_docker_environment_configuration

<!-- badge links -->
[maintained]: https://img.shields.io/maintenance/no/2020
[appd-version]: https://img.shields.io/badge/version-3.0.5-green.svg
[appd-environment]: https://img.shields.io/badge/environment-docker-informational.svg
[hardware]: https://img.shields.io/badge/hardware-rpi3b-important.svg
