Docker parameterized entrypoint
===============================

A Docker entrypoint script that renders templates and runs scripts before
starting the main application.


## Usage

An example Dockerfile:

    FROM nginx

    COPY nginx.conf /templates/etc/nginx/nginx.conf

	ADD https://github.com/jcassee/parameterized-entrypoint/releases/download/0.7.0/entrypoint_linux_amd64 /usr/local/bin/entrypoint
	RUN chmod +x /usr/local/bin/entrypoint

    ENTRYPOINT ["entrypoint", "--"]

    RUN ["nginx", "-g", "daemon off;"]

When you run the container, all environment variables will be available in the
`nginx.conf` template:

	docker run -e domain=www.example.com example/nginx

If using environment variables is inconvenient, for example because the values
are structured, you can set them in `/variables.yml`:

    echo 'domain: www.example.com' > variables.yml
	docker run -v $PWD/variables.yml:/variables.yml example/nginx

Paths can be customized using `entrypoint` command line options. See `entrypoint
-h` for more details.


## Building

    pip install -r requirements.txt
    python setup.py build

The application is available at `dist/entrypoint`.

It is also possible to build the [Alpine Linux](http://alpinelinux.org) binary
using Docker:

    python setup.py build_alpine

The Alpine binary will be saved to `dist/entrypoint-alpine`. In order to use
it, though, you need to add the following directive to your Dockerfile:

    RUN ln -sfn /lib /lib64 && \
        ln -sfn /lib/ld-musl-x86_64.so.1 /lib/ld-linux-x86-64.so.2

(See [this discussion on GitHub](https://github.com/gliderlabs/docker-alpine/issues/48).)
