import argparse
import datetime
from typing import Tuple

import matplotlib.pyplot as plt
import pandas as pd
import requests
from colorama import init, Fore, Back, Style

cli_help_text = 'covidstats.py allows you to view Covid-19 Statistics ' \
                'retrieved from https://covid19api.com/ '

# Create command arguments for the Command Line Interface
parser = argparse.ArgumentParser(description=cli_help_text)

# Arguments for specifying data to be displayed to the user
parser.add_argument('-s', '--summary', action='store_true',
                    help='Get a summary of Covid-19 data')
parser.add_argument('-c', '--chart', action='store_true',
                    help='Create charts alongside data')
parser.add_argument('-d', '--details',
                    help="Get Covid-19 details for a specific country. "
                         "Enter country names in all lower case with a '-' "
                         "for spaces. Use a short form for the country if "
                         "available (ex: usa instead of United States of "
                         "America")
args = parser.parse_args()


def print_data_set(title: str, labels: Tuple[int, int, int]) -> None:
    """
    :param title: Title for data_set
    :param labels: Tuple of 3 string type values containing section labels
    :return: None
    """
    # Print section title
    print(Fore.YELLOW + f'\n{title}: ')

    # Print section labels and the corresponding data
    print(Back.CYAN + Fore.WHITE + Style.BRIGHT + 'Total Confirmed:'
          + Style.RESET_ALL, labels[0])
    print(Back.LIGHTRED_EX + Style.BRIGHT + 'Total Deaths   :'
          + Style.RESET_ALL, labels[1])
    print(Back.GREEN + Style.BRIGHT + 'Total Recovered:'
          + Style.RESET_ALL, labels[2])


def get_data_summary() -> None:
    """
    Print Summary of worldwide Covid-19 Data
    :return: None
    """
    url = 'https://api.covid19api.com/summary'

    print("Loading...", end="\r")

    # Get summary data from the Covid-19 API
    json_data = requests.request("GET", url).json()

    # Print section title to console
    print(Back.WHITE + Fore.BLACK + Style.BRIGHT +
          f' Covid-19 Summary for {datetime.date.today()} '.center(70, '-')
          + Style.RESET_ALL)

    # Help text
    print('Covid-19 Summary for worldwide cases, deaths, and recoveries '
          'add -c \nor --chart to view a graphical representation of the data')

    # Store JSON case data in tuples
    new_case_data = (
        json_data['Global']['NewConfirmed'],
        json_data['Global']['NewDeaths'],
        json_data['Global']['NewRecovered'],
    )

    total_case_data = (
        json_data['Global']['TotalConfirmed'],
        json_data['Global']['TotalDeaths'],
        json_data['Global']['TotalRecovered'],
    )

    # Print Covid-19 All-time totals dating back to "day one"
    print_data_set(title='Totals', labels=total_case_data)

    # Print new Reported Covid-19 cases/deaths/recoveries
    print_data_set(title='New Cases/Deaths/Recoveries', labels=new_case_data)

    # Create a dataframe containing countries with over 100000 cases
    cases_table = pd.DataFrame(json_data['Countries'])
    total_confirmed_table = cases_table[cases_table.TotalConfirmed > 100000]

    # Print totals data for countries with over 100000 confirmed cases
    print(Fore.YELLOW + '\nCovid-19 Data For Countries with over 100000 cases'
          + Fore.MAGENTA)
    print(total_confirmed_table[['Country',
                                 'TotalConfirmed',
                                 'TotalDeaths',
                                 'TotalRecovered']].to_string(index=False))

    # Check if user would like a table representation of the data
    if args.chart:
        # Plot a horizontal bar graph
        total_confirmed_table.plot(kind='barh', x='Country',
                                   y=['TotalConfirmed', 'TotalDeaths',
                                      'TotalRecovered'])

        plt.title('Total Cases By Country')
        plt.xlabel('Cases')
        plt.tight_layout()
        plt.show()

        # Create PieChart for new cases, deaths, and recoveries
        labels = ['Cases', 'Deaths', 'Recovered']
        sizes = [new_case_data[0], new_case_data[1], new_case_data[2]]
        colors = ['lightblue', 'lightcoral', 'yellowgreen']

        # Plot
        plt.pie(sizes, labels=labels, colors=colors,
                autopct=lambda p: '{:.0f}%({:.0f})'.format(p, (p / 100) * sum(
                    new_case_data)))
        plt.title('New Reported Cases, Deaths, and Recovered')
        plt.show()


def get_country_details() -> None:
    """
    Print summary of country specific data including change in cases over time
    :return: None
    """
    url = f'https://api.covid19api.com/total/country/{args.details}'

    print("Loading...", end="\r")

    # Get data by day for a specific country
    json_data = requests.request("GET", url).json()

    # Print details title
    print(Back.WHITE + Fore.BLACK + Style.BRIGHT
          + f' Covid-19 Summary for {args.details} on {datetime.date.today()} '
          .center(70, '-') + Style.RESET_ALL)

    print('Covid-19 details for country specific cases, deaths, and recoveries '
          'add -c \nor --chart to view a graphical representation of the data')

    # Print total case count for specified country
    print_data_set(title='Totals', labels=(
        json_data[-1]['Confirmed'], json_data[-1]['Deaths'],
        json_data[-1]['Recovered']))

    # Get and Display province/state specific data
    print(Fore.YELLOW + f'\nCovid-19 Data For Provinces/States/Cities'
          + Fore.GREEN)

    print("Loading...", end="\r")

    url = f'https://api.covid19api.com/dayone/country/{args.details}/status/confirmed'
    prov_json_data = requests.request("GET", url).json()

    prov_data = pd.DataFrame(prov_json_data)
    # Remove duplicate province entries and get the most recent data
    prov_data = prov_data.drop_duplicates(subset=['Province', 'City'],
                                          keep='last')
    print(prov_data[['Province', 'City', 'Cases']].to_string(index=False))

    # Get data from every week
    country_data = pd.DataFrame(json_data)[::7]
    # Simply Date (Ignore time since all time values are 00:00:00)
    country_data.Date = country_data.Date.str[0:10]

    # Print country_data
    print(Fore.YELLOW + f'\nCovid-19 Data over time for {args.details.title()}'
          + Fore.MAGENTA)
    print(country_data[['Date', 'Confirmed', 'Deaths', 'Recovered']].to_string(
        index=False))

    # Check if user would like a table representation of the data
    if args.chart:
        country_data.plot(kind='line', x='Date',
                          y=['Confirmed', 'Deaths', 'Recovered'])
        plt.title(f'Change in Cases over Time for {args.details.title()}')
        plt.ylabel('Cases')
        plt.tight_layout()
        plt.show()


def main() -> None:
    """
    Run specific blocks of code depending on console arguments
    :return: None
    """
    # init() required to show colored text in the command line for windows
    # operating systems (Ignored by others).
    init()

    # Check for console arguments
    if args.summary:
        get_data_summary()
    elif args.details:
        get_country_details()
    else:
        print(cli_help_text)


if __name__ == "__main__":
    main()