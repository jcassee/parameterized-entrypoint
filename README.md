Docker templating entrypoint
============================

A Docker entrypoint script that renders templates before starting the main
application.


## Usage

An example Dockerfile:

    FROM nginx

    COPY nginx.conf /templates/etc/nginx/nginx.conf

	ADD https://github.com/jcassee/templating-entrypoint/releases/download/0.6.0/entrypoint_linux_amd64 /usr/local/bin/entrypoint
	RUN chmod +x /usr/local/bin/entrypoint

    ENTRYPOINT ["entrypoint"]

    RUN ["nginx", "-g", "daemon off;"]

When you run the container, all environment variables will be available in the
`nginx.conf` template:

	docker run -e domain=www.example.com example/nginx

If using environment variables is inconvenient, for example because the values
are structured, you can also use `/variables.yml`:

	docker run -v $PWD/variables.yml:/variables.yml example/nginx

Paths can be customized using `entrypoint` command line options. See `entrypoint
-h` for more details.


## Building

    pip install -r requirements.txt
    python setup.py build

The application is available at `dist/entrypoint`.
