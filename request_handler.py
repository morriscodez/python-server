from http.server import BaseHTTPRequestHandler, HTTPServer
from animals import get_all_animals, get_single_animal, get_animals_by_location, get_animals_by_status, delete_animal, update_animal, create_animal
from locations import get_all_locations, get_single_location
from customers import get_all_customers, get_single_customer, get_customers_by_email
from employees import get_all_employees, get_single_employee, get_employees_by_location
import json

# Here's a class. It inherits from another class.
# For now, think of a class as a container for functions that
# work together for a common purpose. In this case, that
# common purpose is to respond to HTTP requests from a client.
class HandleRequests(BaseHTTPRequestHandler):

    def parse_url(self, path):
        # Just like splitting a string in JS, if the 
        # path is "/animals/1", the resulting list will
        # have "" at index 0, "animals" at index 1, and "1" 
        # at index 2
        path_params = path.split("/")
        resource = path_params[1]
        
        if "?" in resource:
            #GIVEN: /customers?email=jenna@solis.com

            param = resource.split("?")[1] #email=jenna@solis.com
            resource = resource.split("?")[0] #'customers'
            pair = param.split("=") # [ 'email', 'jenna@solis.com']
            key = pair[0] #email
            value = pair[1] #'jenna@solis.com'

            return (resource, key, value)
        
        # Else if no query string parameter
        else:
            id = None

        # Try to get the item at index 2
            try:
                # Convert the string "1" to the integer 1
                # This is the new parseInt()
                id = int(path_params[2])
            except IndexError:
                pass # No route parameter exists: /animals
            except ValueError:
                pass # Request had trailing slash: /animals/

            return (resource, id) # This is a tuple

    
    
    # Here's a class function
    def _set_headers(self, status):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    # Another method! This supports requests with the OPTIONS verb.
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type, Accept')
        self.end_headers()

    # Here's a method on the class that overrides the parent's method.
    # It handles any GET request.
    def do_GET(self):
        # Set the response code to 'Ok'
        self._set_headers(200)
        response = {} # Default response

        #Parse the URL and store enture tuple in a variable
        parsed = self.parse_url(self.path)

        # Response from parse_url() is a tuple with 2 items
        # which means the request was for '/animals' or '/animals/2'

        if len(parsed) == 2:
            (resource, id ) = parsed


            if resource == "animals":
                if id is not None:
                    response = f"{get_single_animal(id)}"
                else:
                    response = f"{get_all_animals()}"

            if resource == "locations":
                if id is not None:
                    response = f"{get_single_location(id)}"

                else:
                    response = f"{get_all_locations()}"

            if resource == "customers":
                if id is not None:
                    response = f"{get_single_customer(id)}"
                else:
                    response = f"{get_all_customers()}"

            if resource == "employees":
                if id is not None:
                    response = f"{get_single_employee(id)}"
                else:
                    response = f"{get_all_employees()}"

            
            # Response from parse_url() is a tuple with 3 items
            # which means the request was for '/resource?parameter=value'
        elif len(parsed) == 3:
            (resource, key, value) = parsed

            #is the resource 'customers; and was there a query param that specified the customer email as a filtering val?
            if key == "email" and resource == "customers":
                response = get_customers_by_email(value)

            elif key == "location_id" and resource == "animals":
                response = get_animals_by_location(value)

            elif key == "location_id" and resource == "employees":
                response = get_employees_by_location(value)

            elif key == "status" and resource == "animals":
                response = get_animals_by_status(value)

        
        # This weird code sends a response back to the client
        self.wfile.write(response.encode())

    # Here's a method on the class that overrides the parent's method.
    # It handles any POST request.
    def do_POST(self):
        # Set response code to 'Created'
        self._set_headers(201)
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)

        # Convert JSON string to Python dictionary
        post_body = json.loads(post_body)

        # Parse the URL
        (resource, id) = self.parse_url(self.path)

        # Initialize new animal
        new_item = None

        # Add a new item to the list. Don't worry about
        # the orange squiggle, you'll define the create_item
        # function next

        if resource == "animals":
            new_item = create_animal(post_body)

        if resource == "locations":
            new_item = create_location(post_body)

        if resource == "employees":
            new_item = create_employee(post_body)

        if resource == "customers":
            new_item = create_customer(post_body)


        # Encode the new animal and send in response
        self.wfile.write(f"{new_item}".encode())

    # Here's a method on the class that overrides the parent's method.
    # It handles any PUT request.
    def do_PUT(self):
        
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        post_body = json.loads(post_body)

        # Parse url
        (resource, id) = self.parse_url(self.path)

        success = False

        # Delete a single animal from the list
        if resource == "animals":
            success == update_animal(id, post_body)

        if success:
            self._set_headers(204)
        else:
            self._set_headers(404)

            
            # Encode the new animal and send in response
        self.wfile.write("".encode())


    def do_DELETE(self):
        # Set a 204 response code
        self._set_headers(204)

        # Parse the URL
        (resource, id) = self.parse_url(self.path)

        # Delete a single item from the list
        if resource == "animals":
            delete_animal(id)

        if resource == "customers":
            delete_customer(id)

        if resource == "employees":
            delete_employee(id)

        if resource == "locations":
            delete_location(id)

        # Encode the new item and send in response
        self.wfile.write("".encode())

# This function is not inside the class. It is the starting
# point of this application.
def main():
    host = ''
    port = 8088
    HTTPServer((host, port), HandleRequests).serve_forever()

if __name__ == "__main__":
    main()

