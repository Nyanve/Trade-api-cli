import click
import requests
import logging


# base URL for the API, if it doesn't work, replace it with your own URL
base_url = 'http://127.0.0.1:5000/'

logging.basicConfig(filename='cli.log', level=logging.INFO)


@click.command()
@click.option('--name', prompt='Enter the name')
@click.option('--currency', prompt='Enter the base currency')
def create_user_log(name, currency):
    url = f'{base_url}exchanges'  
    data = {
        'name': name,
        'currency': currency,
    }
    response = requests.post(url, json=data)
    if response.status_code == 201:
        click.echo('New created object with exchange_id: ' + str(response.json().get('exchange_id')))
    elif response.status_code == 409:
        click.echo(response.json().get('message'))
    else:
        click.echo('Failed to create object.')


@click.command()
@click.argument('exchange_id', type=int)
@click.option('--amount', type=float, prompt='Enter the amount')
@click.option('--cur_shortcut', prompt='Enter the currency (3-letter shortcut)')
def deposit(exchange_id, amount, cur_shortcut):
    url = f"{base_url}exchanges/{exchange_id}"
    payload = {
        'amount': amount,
        'cur_shortcut': cur_shortcut
    }
    response = requests.post(url, json=payload)
    if response.status_code == 201:
        click.echo('Success')
    elif response.status_code == 409:
        click.echo(response.json().get('message'))
    else:
        click.echo(response.json().get('message'))


@click.command()
@click.argument('exchange_id', type=int)
@click.option('--amount', prompt='Enter the trade amount')
@click.option('--currency_in', prompt='Enter the currency in')
@click.option('--currency_out', prompt='Enter the currency out')
def create_trade(exchange_id, amount, currency_in, currency_out):
    url = f'{base_url}exchanges/{exchange_id}/trades'  # Replace with the correct URL of your API endpoint
    data = {
        'amount': amount,
        'currency_in': currency_in,
        'currency_out': currency_out
    }
    response = requests.post(url, json=data)

    if response.status_code == 201:
        trade_data = response.json()
        click.echo(f'Trade created successfully. Exchanged Amount: {trade_data.get("amount_out")} {trade_data.get("currency_out")}')

    elif response.status_code == 400:
        click.echo(response.json().get('message'))

    else:
        click.echo('Failed to create trade.')



@click.command()
@click.option('--offset', type=int, default=0, help='Offset for pagination')
@click.option('--limit', type=int, default=20, help='Limit for pagination')
@click.option('--exchange_id', type=int, help='Filter trades by specific exchange ID')
@click.option('--search', help='Search query for filtering trades (e.g. "ether")')
@click.option('--date_from', help='Filter trades from this date (YYYY-MM-DD)')
@click.option('--date_to', help='Filter trades up to this date (YYYY-MM-DD)')
def fetch_trade_history(offset, limit, exchange_id, search, date_from, date_to):
    url = f'{base_url}exchanges/history'
    params = {
        'offset': offset,
        'limit': limit,
        'exchange_id': exchange_id,
        'search': search,
        'date_from': date_from,
        'date_to': date_to
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        trades = response.json()
        click.echo('Trade history:')
        for trade in trades:
            click.echo(trade)
    else:
        click.echo('Failed to fetch trade history.')


import click
import requests

@click.command()
@click.argument('exchange_id', type=int)
@click.option('--action', type=click.Choice(['update', 'like', 'unlike']), prompt='Do you want to update, like, or unlike the currency?')
def bulk_action(exchange_id, action):
    cur_shortcuts = []

    while True:
        cur = click.prompt('Enter the currency (3-letter shortcut) or "stop" to finish', type=str)
        if cur.lower() == 'stop':
            break
        cur_shortcuts.append(cur)

    for cur in cur_shortcuts:
        if action == 'update':
            logging.info(f'Updating currency {cur}')
            # Call the /update_currency endpoint
            update_url = f"{base_url}update_currency"
            update_payload = { 
                'cur_shortcut': cur,
            }
            update_response = requests.post(update_url, json=update_payload)
            
            if update_response.status_code == 200:
                click.echo(f"Currency {cur} updated successfully.")
            else:
                click.echo("Failed to update currency.")
   
        elif action == 'like':
            logging.info(f'Liking currency {cur}')
            # Call the /add_to_liked endpoint
            like_url = f"{base_url}add_to_liked"
            like_payload = {
                'cur_shortcut': cur,
                'exchange_id': exchange_id
            }
            like_response = requests.post(like_url, json=like_payload)
            if like_response.status_code == 200:
                click.echo(f'Currency {cur} added to liked list')
            elif like_response.status_code == 409:
                click.echo(like_response.json().get('message'))
            elif like_response.status_code == 404:
                click.echo(like_response.json().get('message'))
            else:
                click.echo(like_response.json().get('message'))

        elif action == 'unlike':
            logging.info(f'Unliking currency {cur}')
            # Call the /remove_from_liked endpoint
            remove_url = f"{base_url}remove_from_liked"
            remove_payload = {
                'cur_shortcut': cur,
                'exchange_id': exchange_id
            }
            remove_response = requests.post(remove_url, json=remove_payload)
            if remove_response.status_code == 200:
                click.echo(f'Currency {cur} removed from liked list')
            elif remove_response.status_code == 409:
                click.echo(remove_response.json().get('message'))
            elif remove_response.status_code == 404:
                click.echo(remove_response.json().get('message'))
            else:
                click.echo(remove_response.json().get('message'))


@click.group()
def cli():
    pass

cli.add_command(create_user_log)
cli.add_command(deposit)
cli.add_command(create_trade)
cli.add_command(fetch_trade_history)
cli.add_command(bulk_action)

if __name__ == '__main__':
    cli()