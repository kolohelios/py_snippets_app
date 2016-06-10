import logging
import argparse
import psycopg2

# Set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)

logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect(database="snippets")
logging.debug("Database connection established.")

def put(name, snippet, hidden):
    '''
    Store a snippet with an associated name.
    Return the snippet if found or return a 404:Snippet Not Found error
    '''
    logging.info('Storing snippet {!r}: {!r} hidden:{!r}'.format(name, snippet, hidden))
    with connection, connection.cursor() as cursor:
        try:
            command = 'insert into snippets values (%s, %s, %s)' 
            cursor.execute(command, (name, snippet, hidden))
        except psycopg2.IntegrityError as e:
            connection.rollback()
            command = 'update snippets set message=%s, hidden=%s where keyword=%s'
            cursor.execute(command, (snippet, hidden, name))
    logging.debug('Snippet stored successfully.')
    return name, snippet
    
def get(name):
    '''
    Retrieve the snippet with a given name.
    If there is no such snippet, return '404: Snippet Not Found'.
    '''
    logging.info('Retrieving snippet {!r}'.format(name))
    with connection, connection.cursor() as cursor:
        cursor.execute('select message from snippets where keyword=%s', (name,))
        row = cursor.fetchone()
    if not row:
        # no snippet was found with that name
        return '404: Snippet Not Found'
    return row[0]
    
def catalog():
    '''
    Get a catalog of snippet keywords from the database.
    '''
    
    logging.info('Fetching catalog')
    with connection, connection.cursor() as cursor:
        cursor.execute("select keyword from snippets where not hidden order by keyword")
        keywords = cursor.fetchall()
    return keywords
    
def search(term):
    '''
    Using a search term search the database.
    '''
    
    logging.info('Searching database')
    with connection, connection.cursor() as cursor:
        term = '%' + term + '%'
        cursor.execute("select * from snippets where (keyword like %s or message like %s) and not hidden group by keyword",(term,term))
        matches = cursor.fetchall()
    return matches

def main():
    '''Main function'''
    logging.info('Constructing parser')
    parser = argparse.ArgumentParser(description = 'Store and retrieve snippets of text')
    
    subparsers = parser.add_subparsers(dest = 'command', help = 'Available commands')

    # subparser for the put command
    logging.debug('Constructing put subparser')
    put_parser = subparsers.add_parser('put', help = 'Store a snippet')
    put_parser.add_argument('name', help = 'Name of the snippet')
    put_parser.add_argument('snippet', help = 'Snippet text')
    put_parser.add_argument('--hidden', help = 'Hide snippet', action = 'store_true')
    
    get_parser = subparsers.add_parser('get', help = 'Retrieve a snippet')
    get_parser.add_argument('name', help = 'Name of the snippet')
    
    get_parser = subparsers.add_parser('catalog', help = 'Get a list of all keywords')
    
    get_parser = subparsers.add_parser('search', help = 'Search for a term')
    get_parser.add_argument('term', help = 'Term to search for')

    arguments = parser.parse_args()
    
    arguments = vars(arguments)
    print(arguments)
    command = arguments.pop('command')
    
    if command == 'put':
        name, snippet = put(**arguments)
        print('Store {!r} as {!r}'.format(snippet, name))
    elif command == 'get':
        snippet = get(**arguments)
        print('Retrieved snippet: {!r}'.format(snippet))
    elif command == 'catalog':
        keywords = catalog()
        print('Fetching catalog')
        print('----------------')
        for keyword in keywords:
            print(keyword[0])
    elif command == 'search':
        matches = search(**arguments)
        print('Fetching matches')
        print('--------------------------------------')
        print('keyword    message')
        print('--------------------------------------')
        for match in matches:
            print(match[0].ljust(10), match[1])
    
if __name__ == '__main__':
    main()
    