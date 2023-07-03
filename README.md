# REST API with Flask, SQLAlchemy and CLI interface


## Installation

To install and run the Trade API, please follow the steps below:

1. Clone the repository from GitHub: https://github.com/Nyanve/Trade-api-cli.git

2. Create a virtual environment and activate it:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the required packages:

   ```bash
    pip install -r requirements.txt
    ```
4. Run the application:

   ```bash
   flask run
   ```
5. Run the tests:

   ```bash
   python test_script.py
   ```   
   (This could take some time because the database is also being populated)
6. Its ready to use!

        

## Description

All endpoints are located in resources folder with description. They are accesiible via swager UI on your_url/swagger-ui.
Also trought API platforms like Postman or Insomnia. 
The requested endpoints are accessible via CLI interface. To use it, please follow the steps below:
To create a user log:
```bash
python cli.py create-user-log 
```

To deposit funds:
```bash
python cli.py deposit 1 (where 1 is the exchange_id)
```

To create a trade:
```bash
python cli.py create-trade 1 (where 1 is the exchange_id)
```

To fetch the trade history:
```bash
python cli.py fetch-trade-history --offset 0 --limit 10 --exchange_id 1 --search "BTC" --date_from "YYYY-MM-DD" --date_to "YYYY-MM-DD"
```
(You can use any combination of the parameters above, or none of them for the default values)

To acces the bulk action:
```bash
python cli.py bulk-action 1 (where 1 is the exchange_id, then you will be asked to choose the action) 
```

If you want to see the help message, please run:
```bash
python your_script_name.py --help
```










