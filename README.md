<a name="readme-top"></a>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/Pavkv/PlayStationStoreDiscountBot">
    <img src="images/logo.webp" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">PlayStation Store Discount Bot</h3>

  <p align="center">
    A Telegram bot for tracking PlayStation Store game discounts and managing game wishlists.
    <br />
    <a href="https://github.com/Pavkv/PlayStationStoreDiscountBot"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/Pavkv/PlayStationStoreDiscountBot">View Demo</a>
    ·
    <a href="https://github.com/Pavkv/PlayStationStoreDiscountBot/issues">Report Bug</a>
    ·
    <a href="https://github.com/Pavkv/PlayStationStoreDiscountBot/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

<img src="images/example_screenshot.png" alt="example">

The PS Store Bot is a Telegram bot designed to help users keep track of PlayStation Store game discounts, manage their wishlist of games, and receive updates on price changes. It leverages the PlatPrices API for real-time data on game prices and discounts.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* Python 3.6+
* SQLite3
* A Telegram bot token (You can get one through <a href="https://t.me/BotFather">BotFather</a> on Telegram)
* A PlatPrices API key (You can get one by signing up on the <a href="#https://platprices.com/developers.php">Plat Prices</a> website)

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/Pavkv/PlayStationStoreDiscountBot
   ```
3. Install required packages
   ```sh
   pip install -r requirements.txt
   ```
4. Set up environment variables in `.env` file
   ```sh
    TELEGRAM_TOKEN=your_telegram_bot_token
    API_KEY=your_platprices_api_key
    DATABASE_URL=your_database_url
   ```
5. Initialize the database
   ```sh
   python init_db.py
   ```
6. Run the bot
   ```sh
    python bot.py
    ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

After starting the bot, you can interact with it on Telegram:

* Send /start to begin interacting with the bot.
* Follow the prompts to add games to your wishlist, delete games, or check for current discounts.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- Scheduled Tasks -->
## Scheduled Tasks

The bot automatically checks for discounts on wishlist games every Monday at 13:00 UTC. Ensure the bot is running to receive these notifications.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- Logging -->
## Logging

The bot logs its operations and errors to PSStoreBot.log. Check this file for troubleshooting and monitoring bot activity.

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Pasha Zobov - [Linked In](https://www.linkedin.com/in/pavel-zobov-3a6365230/)

Project Link: [https://github.com/Pavkv/PlayStationStoreDiscountBot]([https://github.com/Pavkv/PlayStationStoreDiscountBot])

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/Pavkv/PlayStationStoreDiscountBot.svg?style=for-the-badge
[contributors-url]: https://github.com/Pavkv/PlayStationStoreDiscountBot/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Pavkv/PlayStationStoreDiscountBot.svg?style=for-the-badge
[forks-url]: https://github.com/Pavkv/PlayStationStoreDiscountBot/network/members
[stars-shield]: https://img.shields.io/github/stars/Pavkv/PlayStationStoreDiscountBot.svg?style=for-the-badge
[stars-url]: https://github.com/Pavkv/PlayStationStoreDiscountBot/stargazers
[issues-shield]: https://img.shields.io/github/issues/Pavkv/PlayStationStoreDiscountBot.svg?style=for-the-badge
[issues-url]: https://github.com/Pavkv/PlayStationStoreDiscountBot/issues
[license-shield]: https://img.shields.io/github/license/Pavkv/PlayStationStoreDiscountBot.svg?style=for-the-badge
[license-url]: https://github.com/Pavkv/PlayStationStoreDiscountBot/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/pavel-zobov-3a6365230/
[product-screenshot]: images\example_screenshot.png
