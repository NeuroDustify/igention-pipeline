# Smart Dustbin Project - Suburb Model and Data Generation

This project provides a basic, decoupled structure for modeling a suburban area and generating simulated data for its components (Houses, Streets, Driveways, Suburb). It also includes a script to publish this generated data to an MQTT broker.

The project is organized into the following directories:

* `suburb_model/`: Contains the Python classes that define the structure of the suburb (Location, Driveway, House, Street, Suburb).
* `data_generator/`: Contains the Python script to generate simulated data based on the suburb model classes and save it to CSV files.
* `mqtt_publisher/`: Contains the Python script to read the generated data from CSVs and publish it to an MQTT broker.
* `generated_data/`: This directory will be created by the data generator script and will contain the output CSV files.

## Setup

1.  **Clone or Download:** Get the project files. If you ran the bash script to create the structure, you already have the basic setup.
2.  **Navigate to Project Root:** Open your terminal or command prompt and navigate to the `smart_dustbin_project` directory.
3.  **Install Dependencies:** You need the `paho-mqtt` library for the MQTT publisher.
    ```bash
    pip install paho-mqtt
    ```
4.  **Configure MQTT Publisher:**
    * Go to the `mqtt_publisher/` directory.
    * Open the `publish_suburb_data.py` file.
    * Replace the placeholder values for `MQTT_BROKER_ADDRESS`, `MQTT_USERNAME`, and `MQTT_PASSWORD` with your actual HiveMQ Cloud broker details.

## Usage

1.  **Generate Data:**
    * Navigate back to the **project root** directory (`smart_dustbin_project/`).
    * Run the data generator script:
        ```bash
        python -m data_generator.generate_suburb_data
        ```
    * Follow the on-screen menu to generate data for Driveways, Houses, Streets, and the Suburb in that order to respect dependencies. The data will be saved in the `generated_data/` directory.

2.  **Publish Data via MQTT:**
    * Ensure your MQTT broker (e.g., HiveMQ Cloud) is running and accessible.
    * Ensure you have generated data in the `generated_data/` directory.
    * Navigate back to the **project root** directory (`smart_dustbin_project/`).
    * Run the MQTT publisher script:
        ```bash
        python -m mqtt_publisher.publish_suburb_data
        ```
    * Follow the on-screen menu to select which data you want to publish to your MQTT broker.

## Extending the Model

* You can add more attributes or methods to the classes in the `suburb_model/` directory as needed (e.g., adding `bins` attribute to `Driveway` or `House`, adding geographical boundaries to `Street` or `Suburb`).
* Update the `data_generator/generate_suburb_data.py` script to generate data for any new attributes.
* Update the `mqtt_publisher/publish_suburb_data.py` script if you need to publish the new data via MQTT.

This decoupled structure makes it easier to manage and extend different parts of your smart dustbin project independently.
