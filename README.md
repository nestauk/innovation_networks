# Innovation Networks Data Pilot

This repository contains the entirety of the Innovation Networks Data Pilot. That includes all code required to reproduce the pilot and outputs from analyses.

Here's the repository structure:

- README.md
- LICENSE.txt
- requirements.txt
- __innovation-networks__
  - \__init\__.py
  - __data__
    - error_names.txt
    - towns_and_cities_2015.txt
  - __data_gathering__
    - __github__
      - \__init\__.py
      - get_data.py
      - parse_users.py
      - user_at_location.py
- __tests__
    - \__init__\.py
    - __test_github__
      - \__init\__.py
      - test_data.json.gz
      - test_error_data.json
      - test_get_data.py
      - test_parse_users.py
      - test_user_data.json

To replicate the pilot, follow these instructions:

1. Clone this repo using `git clone https://github.com/nestauk/innovation_networks.git`
2. Install python dependencies `pip install -r requirements.txt`
3. Run `python innovation_networks/data_gathering/github/get_data.py`. This will gather the GitHub event stream for the last 2 years from https://www.githubarchive.org/.
4. Run `python innovation_networks/data_gathering/github/parse_user.py 'absolute/path/to/datafile/' 'absolute/path/to/output/directory'`. This will take the event data and parse it for unique users, storing the output as JSON.
in the format

    ```JSON
    [{"user": "username", "attributes":{"attribute": "value", "attribute": "value"}}, {"user":"username", "attributes": {"attribute": "value"}]
    ```

5. Run `python innovation_networks/data_gathering/github/users_at_location.py 'absolute/path/to/placenames' 'absolute/path/to/error/names' 'absolute/path/to/user/data' 'absolute/path/to/outfile`. Placenames should be a plain text file of places to match against, one location per line. The file `town_and_cities_2015.txt` is a good example of this. An extra step for removal of names from different countries will probably be required. For this, add error names to the file `error_names.txt`. The example in this repository removes errors we found in our analysis. You will need to update this for your own needs.
