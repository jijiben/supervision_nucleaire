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
- View the average values per hour and the sum of values per hour of each day.
- The data is visualized using charts.

## API Documentation

- The app retrieves data from the RTE API. Refer to the [API documentation](https://data.rte-france.com/catalog/-/api/doc/user-guide/Actual+Generation/1.1) for more information on the API endpoints and parameters.
- The used enpoint is: /actual_generations_per_unit

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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.