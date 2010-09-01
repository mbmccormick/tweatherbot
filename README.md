# tweatherbot

Twitter API integration delivering local weather reports throughout the day.


## Requirements

tweatherbot is a small Google AppEngine service that publishes local weather reports to Twitter.


## Installation

This service is designed to be run on the Google AppEngine development platform. The scripts and configuration files can only be run from a desktop environment through the use of the Google AppEngine SDK.

Twitter account information, for the robots, and associated Weather Underground iCal feeds are stored in the GQL datastores on Google AppEngine. This allows for more robots to be added, without having to rebuild or modify the tweatherbot service.


## Usage

This service is self-sustaining, meaning that once the scripts and configuration files are loaded on the Google AppEngine servers, no additional maintenance or overhead is necessary.

tweatherbot pings Weather Underground's iCal feeds for the latest forecasts and publishes new reports when an update is available.


## Disclaimer

Use this service at your own risk. While this service has been tested thoroughly, on the above requirements, your mileage may vary. I take no responsibility for any harmful actions this service might cause.


## License

This software, and its dependencies, are distributed free of charge and licensed under the GNU General Public License v3. For more information about this license and the terms of use of this software, please review the LICENSE.txt file.
