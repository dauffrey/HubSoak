HubSoak
An advanced water quality monitoring system for your hot tub, powered by Raspberry Pi 5. HubSoak provides real-time tracking of essential water metrics such as pH, temperature, turbidity, ORP, conductivity, chlorine levels, bromine, and UV intensity. The system features an interactive touchscreen interface built with Streamlit, offering maintenance scheduling, remote access, and comprehensive data visualization.
________________________________________
Table of Contents
•	Features
•	Demo
•	Getting Started
o	Hardware Requirements
o	Software Requirements
•	Installation
o	1. Setting Up the Raspberry Pi 5
o	2. Connecting the Sensors
o	3. Cloning the Repository
o	4. Installing Dependencies
o	5. Running HubSoak
•	Usage
o	Monitor Tab
o	Maintain Tab
o	Remote Tab
•	Data Visualization
•	Calibration
•	Maintenance
•	Safety Precautions
•	Contributing
•	License
•	Acknowledgments
________________________________________
Features
•	Real-Time Monitoring: Continuously displays current levels of pH, temperature, turbidity, ORP, conductivity, free chlorine, total chlorine, bromine, and UV intensity.
•	Historical Data Logging: Stores sensor data in a local SQLite3 database for trend analysis.
•	Interactive Touchscreen Interface: Easy-to-use GUI built with Streamlit, optimized for touch interaction.
•	Data Visualization: Generate interactive graphs and charts to analyze water quality over time.
•	Maintenance Scheduling: Keep track of regular maintenance tasks with reminders and logs.
•	Remote Access: Securely access your hot tub's data remotely with encrypted connections.
•	Alerts and Recommendations: Receive alerts when parameters are out of range and get actionable recommendations.
________________________________________
Demo
Note: Include screenshots or a link to a demo video showcasing the application's interface and features.
________________________________________
Getting Started
Hardware Requirements
•	Raspberry Pi 5 with power supply
•	7-inch Touchscreen Display compatible with Raspberry Pi
•	MicroSD Card (16GB or larger)
•	Sensors:
o	pH Sensor Kit (with BNC connector and signal converter)
o	DS18B20 Waterproof Digital Temperature Sensor
o	Turbidity Sensor (analog output)
o	ORP Sensor
o	Conductivity/TDS Sensor
o	Free Chlorine Sensor
o	Total Chlorine Sensor
o	Bromine Sensor
o	UV Intensity Sensor
•	Analog-to-Digital Converter (ADC): MCP3008 or similar
•	Breadboard and Jumper Wires
•	4.7kΩ Resistor (for DS18B20 sensor)
•	Protective Enclosure (optional but recommended)
Software Requirements
•	Raspberry Pi OS (latest version)
•	Python 3
•	Git
•	Required Python Libraries:
o	streamlit
o	plotly
o	pandas
o	numpy
o	sqlite3
o	RPi.GPIO
o	gpiozero
o	spidev
o	adafruit-circuitpython-mcp3xxx
________________________________________
Installation
1. Setting Up the Raspberry Pi 5
a. Install Raspberry Pi OS
1.	Download the latest Raspberry Pi OS from the official website.
2.	Use the Raspberry Pi Imager to flash the OS onto the microSD card.
3.	Insert the microSD card into the Raspberry Pi.
b. Initial Configuration
1.	Connect the touchscreen display to the Raspberry Pi.
2.	Power on the Raspberry Pi and complete the setup wizard.
3.	Update the system packages:
bash
Copy code
sudo apt update && sudo apt upgrade -y
4.	Enable necessary interfaces:
bash
Copy code
sudo raspi-config
o	Navigate to Interface Options and enable I2C, SPI, and 1-Wire.
2. Connecting the Sensors
Refer to the sensor datasheets for detailed wiring instructions.
a. pH Sensor Connection
•	Components: pH probe, signal converter board, MCP3008 ADC.
•	Wiring:
o	Connect the pH probe to the signal converter.
o	Connect the signal converter's output to CH0 on the MCP3008.
o	Connect the MCP3008 to the Raspberry Pi via SPI.
b. Temperature Sensor Connection (DS18B20)
•	Wiring:
o	Red wire to 3.3V.
o	Black wire to Ground.
o	Yellow wire to GPIO4 (pin 7).
o	Place a 4.7kΩ resistor between the red and yellow wires.
c. Additional Sensors
•	Turbidity Sensor: Connect analog output to CH1 on the MCP3008.
•	ORP Sensor: Connect to CH2 on the MCP3008.
•	Conductivity/TDS Sensor: Connect to CH3 on the MCP3008.
•	Free Chlorine Sensor: Connect to CH4 on the MCP3008.
•	Total Chlorine Sensor: Connect to CH5 on the MCP3008.
•	Bromine Sensor: Connect to CH6 on the MCP3008.
•	UV Intensity Sensor: Connect to CH7 on the MCP3008.
d. MCP3008 ADC Connection
•	Wiring:
o	VDD and VREF to 3.3V.
o	AGND and DGND to Ground.
o	CLK to GPIO11 (pin 23).
o	DOUT to GPIO9 (pin 21).
o	DIN to GPIO10 (pin 19).
o	CS to GPIO8 (pin 24).
3. Cloning the Repository
bash
Copy code
git clone https://github.com/dauffrey/HubSoak.git
cd HubSoak
4. Installing Dependencies
Install required Python libraries:
bash
Copy code
sudo apt install python3-pip
pip3 install -r requirements.txt
Ensure the requirements.txt file includes all necessary libraries.
5. Running HubSoak
Start the Streamlit application:
bash
Copy code
streamlit run main.py
________________________________________
Usage
The application is divided into three main tabs: Monitor, Maintain, and Remote.
Monitor Tab
•	Real-Time Metrics: View current readings of all sensors.
•	Alerts and Recommendations:
o	Receive alerts when parameters are out of optimal ranges.
o	Get actionable recommendations to correct any issues.
•	Historical Data Visualization:
o	Expandable sections for each sensor with interactive graphs.
o	View current, average, and historical values.
•	Calibration Controls:
o	Adjust sensor calibration from the sidebar controls.
Maintain Tab
•	Maintenance Tasks:
o	View upcoming maintenance tasks.
o	Mark tasks as complete and add notes.
•	Add New Tasks:
o	Add custom maintenance tasks with descriptions and frequencies.
•	Task History:
o	View the completion history of maintenance tasks.
Remote Tab
•	Remote Access Information:
o	Secure access URL for remote monitoring.
o	Security features like HTTPS encryption and activity logging.
•	Recent Access Logs:
o	View recent remote access attempts.
•	Settings:
o	Enable email alerts for remote access.
o	Adjust refresh intervals.
________________________________________
Data Visualization
•	Interactive Graphs: Zoom, pan, and hover over data points for detailed information.
•	Sensor History: View historical data for the past 12 hours or adjust the timeframe.
•	Data Export: Optionally implement data export features for further analysis.
________________________________________
Calibration
Calibration is crucial for accurate readings. Use the sidebar controls to adjust the offset and scale for each sensor.
Steps:
1.	Select Sensor: Choose the sensor you wish to calibrate.
2.	Adjust Offset and Scale: Input the calibration values based on standard solutions or reference measurements.
3.	Apply Changes: Click the "Apply" button to update the calibration settings.
Note: Calibration procedures may vary for each sensor. Refer to the sensor manufacturer's guidelines.
________________________________________
Maintenance
•	Regular Cleaning: Clean sensors to prevent fouling and ensure accurate readings.
•	Software Updates: Keep the system updated for new features and security patches.
•	Data Backup: Regularly back up the hubsoak.db database to prevent data loss.
________________________________________
Safety Precautions
•	Electrical Safety: Ensure all electrical connections are secure and insulated to prevent short circuits.
•	Waterproofing: Use waterproof enclosures for components exposed to moisture.
•	GFCI Protection: Power the system through a Ground Fault Circuit Interrupter.
•	Professional Assistance: Consult professionals for installation if you are not experienced with electrical systems.
________________________________________
Contributing
Contributions are welcome! Please follow these steps:
1.	Fork the Repository: Click the "Fork" button on the GitHub repository.
2.	Create a Branch: Use git checkout -b feature/YourFeatureName.
3.	Commit Your Changes: Use descriptive commit messages.
4.	Push to the Branch: Use git push origin feature/YourFeatureName.
5.	Open a Pull Request: Describe your changes and submit the PR.
________________________________________
License
This project is licensed under the MIT License. See the LICENSE file for details.
________________________________________
Acknowledgments
•	Raspberry Pi Foundation: For the Raspberry Pi hardware and software.
•	Sensor Manufacturers: For providing quality sensors and documentation.
•	Streamlit Community: For the powerful and user-friendly web application framework.
•	Contributors: Thanks to everyone who has contributed to the development of HubSoak.
________________________________________
Note: Always ensure compliance with local regulations and safety standards when implementing HubSoak. The developers are not liable for any damage or injury resulting from the use of this system.
________________________________________
For any questions or support, please open an issue on the GitHub repository.

