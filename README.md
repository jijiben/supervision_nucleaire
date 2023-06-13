# Flask supervision nucleaire App

The Flask supervision-nucleaire App is a web application that retrieves and displays actual generation data for nuclear power units within a specified date range. It provides various statistics and visualizations based on the data.


## Features

- Retrieve actual generation data for nuclear power units.
- Calculate average values per hour.
- Calculate sum of values per hour of each day.
- Visualize the data using charts.

## Development Languages

- Python 3.9
- JavaScript

## Installation

1. Clone the repository:

   ```shell
   $ https://github.com/jijiben/supervision_nucleaire.git
   ```

2. Install the required dependencies:
   using poetry
   ```shell
   $ cd supervision-nucleaire
   $ poetry shell
   $ poetry install
      ```
   using your virtual env and pip
   ```shell
   $ cd supervision-nucleaire
   $ pip install -r requirements.txt
   
   ```

3. Configure the app:

   - Obtain an API key from the RTE website (https://data.rte-france.com/).
   - Update the `config.py` file with your API key.

4. Run the app:

   ```shell
   $ python app.py
   ```
   The app will be accessible at `http://localhost:5000`.

## Usage

- Access the web app in your browser at `http://localhost:5000`.
- The default date range is set to 01/12/2022 to 10/12/2022.
- To view data for a custom date range, you can modify the start and end dates by appending the `start_date` and `end_date` query parameters to the URL. The dates should be in ISO format.
  - Example for end route '/': `http://localhost:5000/?start_date=2022-11-01T00:00:00%2B02:00&end_date=2022-11-11T00:00:00%2B02:00`
  - Example for end route '/data': `http://localhost:5000/data?start_date=2022-11-01T00:00:00%2B02:00&end_date=2022-11-11T00:00:00%2B02:00`
- The data will be updated based on the specified date range.
- View the average values per hour and the sum of values per hour of each day.
- The data is visualized using charts:

  1. **Sum of Infra-Hourly Production per Hour of the Day**: This chart shows the total production for each hour of the day over the selected date range.

  2. **Average Production per Hour**: This chart displays the average production per hour over the selected date range.

    The charts are automatically updated every 24 hours. You can also manually refresh the charts by clicking the refresh button.

## API Documentation

- The app retrieves data from the RTE API. Refer to the [API documentation](https://data.rte-france.com/catalog/-/api/doc/user-guide/Actual+Generation/1.1#_Toc506996007) for more information on the API endpoints and parameters.
- The used endpoint is: `/actual_generations_per_unit`.
- The API provides one value per time interval, following the rules:
  - AGPU-RG07: There is no handling of daylight saving time changes.
  - The service always returns 24 values, one value per hour.

## Testing

- Test are defined under Unitest library

## Bonus

- Implement real-time refreshing of the interface on a rolling daily period.
  - Feel free to modify it under templates\index.html: setInterval(refreshCharts, 86400000);
      - The setInterval() method calls a function at specified intervals (in milliseconds).

## Deployed Application

- The application is deployed on Heroku and can be accessed at the following links:
  - [Flask supervision-nucleaire App](https://supervision-nucleaire.herokuapp.com/)
  - [Data Endpoint](https://supervision-nucleaire.herokuapp.com/data)

## Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please feel free to contribute.

I personally enjoyed working on this project, and I hope that it showcases my skills and enthusiasm for the position. I am highly motivated to work with your team and contribute to the success of the project.

Thank you for considering my application, and I look forward to the opportunity to work together!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.