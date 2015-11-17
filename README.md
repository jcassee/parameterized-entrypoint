Docker templating entrypoint
============================

A Docker entrypoint script that renders templates using environment variables
before starting the main application.


## Building

    pip install -r requirements.txt
    python setup.py build

The application is available at `dist/entrypoint`.


## Usage

An example Dockerfile:

    FROM nginx

    COPY nginx.conf /templates/etc/nginx/nginx.conf
	ADD https://github.com/jcassee/templating-entrypoint/releases/download/0.3.0/entrypoint_linux_amd64 /usr/local/bin/entrypoint
	RUN chmod +x /usr/local/bin/entrypoint

    ENTRYPOINT ["entrypoint", "/templates", "/"]

    RUN ["nginx", "-g", "daemon off;"]

When you run the container, all environment variables will be available in the
`nginx.conf` template.
