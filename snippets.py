import logging
import argparse
import psycopg2

# Set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)

logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect(database="snippets")
logging.debug("Database connection established.")

def put(name, snippet):
    '''
    Store a snippet with an associated name.
    Return the snippet if found or return a 404:Snippet Not Found error
    '''
    logging.info('Storing snippet {!r}: {!r}'.format(name, snippet))
    with connection, connection.cursor() as cursor:
        try:
            command = 'insert into snippets values (%s, %s)' 
            cursor.execute(command, (name, snippet))
        except psycopg2.IntegrityError as e:
            connection.rollback()
            command = 'update snippets set message=%s where keyword=%s'
            cursor.execute(command, (snippet, name))
    logging.debug('Snippet stored successfully.')
    
    # logging.error('FIXME: Unimplemented - put({!r}, {!r})'.format(name, snippet))
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
    
    # logging.error('FIXME: Unimplemented - get({!r})'.format(name))

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
    
    get_parser = subparsers.add_parser('get', help = 'Retrieve a snippet')
    get_parser.add_argument('name', help = 'Name of the snippet')

    arguments = parser.parse_args()
    
    arguments = vars(arguments)
    command = arguments.pop('command')
    
    if command == 'put':
        name, snippet = put(**arguments)
        print('Store {!r} as {!r}'.format(snippet, name))
    elif command == 'get':
        snippet = get(**arguments)
        print('Retrieved snippet: {!r}'.format(snippet))
    
if __name__ == '__main__':
    main()
    