Python Packagers
==========================================

This repo contains the code and steps that I went through in trying to
compare different packaging solutions for pythoon.  I will also list
my thoughts after using each one.  

To try to create a fair comparison I am going to create a simple project
that should be able to be packaged (act like a library) as well as
started as an application.  To that end I am going to create a simple
hello world application.  

## Poetry

Poetry is a tool that I have used for a while on a personal project after
I stopped using pipenv because of its dependency resolution issues that I
had encountered.  

### Installation

I installed poetry globally using pip.  

        pip install -U poetry

### Project Setup

I created the new package using the poetry setup command.  

        poetry new poetry-app

I then navigated to the folder that was created and created a virtual environment
for me to use.  

        cd poetry-app
        python3 -m venv .venv
        ln -s .venv/bin/activate activate
        source activate

Once the virtual environment was created I installed poetry using the default
configuration (no changes yet).  

        poetry install

**NOTE: I did not try the automatic venv setup that poetry says it will do so I
cannot comment on how wells it works**

The installation process was super fast and had the following output.   

        Updating dependencies
        Resolving dependencies... (4.5s)

        Package operations: 7 installs, 0 updates, 0 removals

        Writing lock file
          - Installing six (1.11.0)
          - Installing atomicwrites (1.2.1)
          - Installing attrs (18.2.0)
          - Installing more-itertools (4.3.0)
          - Installing pluggy (0.7.1)
          - Installing py (1.6.0)
          - Installing pytest (3.8.0)

So everything looked fine for the first setup.  

### Project Code

The first step for our code portion was to add flask as a dependencies, 
so I did this using the poetry tools.  

        poetry add flask requests

This added a section to the `pyproject.toml` file.  

        requests = "^2.19"
        flask = "^1.0"

I really like that it pinned to the version (allowing upper versions) by default
instead of "*" as used in pipenv.   

I then installed `pylint` as a dev dependency using this command.  

        poetry add -D pylint

So far so good.  So now I copied the following two pieces of code, the app.py (which
is the rest endpoint) as well as the client.py.  `app.py` is placed at the root of the
project, since it is not a packaged py file that I want added in the final deploy, and
`client.py` is the only file (next to `__init__.py`) that goes in the package folder.  

So at this point to start the server it is simply...

        python app.py

We now need to consume a client, but we want to build a package so lets go through
that process.  

### Creating a Package

Luckily, with poetry, it is easy to build a wheel.  This just requires that you run
the following command.  

        poetry build

When run on my project I had the following output.   

        Building poetry-app (0.1.0)
         - Building sdist
         - Built poetry-app-0.1.0.tar.gz

         - Building wheel
         - Built poetry_app-0.1.0-py2.py3-none-any.whl

Both these files were placed un the `dist` folder.  You can also publish by using
this command (**NOTE: I did not try to publish to pypi so this is from docs**)

        poetry publish
        
        # To our nexus
        poetry publish -r pypi-internal

### Package Test

I now created a side project `poetry-consumer` that installs the built wheel and
tries to consume the endpoint when it is running.  

        mkdir poetry-consumer
        cd poetry-consumer
        python3 -m venv .venv
        source .venv/bin/activate
        pip install ../poetry-app/dist/*.whl
        
Ok lets check what got installed and make sure none of our dev dependencies are there.  

        certifi==2018.8.24
        chardet==3.0.4
        click==6.7
        Flask==1.0.2
        idna==2.7
        itsdangerous==0.24
        Jinja2==2.10
        MarkupSafe==1.0
        pkg-resources==0.0.0
        poetry-app==0.1.0
        requests==2.19.1
        urllib3==1.23
        Werkzeug==0.14.1

Yep, looks good to me.  

## Hatch

So the next tool I wanted to try is Hatch.  This has more stars than poetry, however it
hasn't been updated in a while (Jun 28th of this year).  So I am going to follow the same
sections to have a comparison.   

### Installation

I started by installing hatch using the below command.  

        pip3 install -U hatch

This installed the version `0.20` but it also installed A LOT of other dependencies that
didn't exist when poetry was installed.  Here is the list.  


        Installing collected packages: wheel, appdirs, six, more-itertools, atomicwrites, py, attrs, pluggy, setuptools, pytest, virtualenv, colorama, click, urllib3, idna, certifi, chardet, requests, requests-toolbelt, tqdm, pkginfo, twine, ptyprocess, pexpect, pip, coverage, adduserpath, semver, hatch

### Project Setup

To setup the project I used the hatch creation command `new`.   

        hatch new hatch-app

So the first thing that came out was that it looks like it created a virtual environment
for the system (but I don't know where) as well as installing at the time of creation.  

        Created project `hatch-app`
        Creating its own virtual env... complete!
        Installing locally in the virtual env... complete!

So I then navigated to the folder for the hatch project and it is surprising the structure
that is provides.  

        .coveragerc
        .git
        .gitattributes
        .gitignore
        hatch_app
        hatch_app.egg-info
        LICENSE-APACHE
        LICENSE-MIT
        MANIFEST.in
        pyproject.toml
        README.rst
        requirements.txt
        setup.py
        tests
        tox.ini
        venv

Very interesting that it provides 2 license types by default, but instead of replacing the
`requirements.txt`, `setup.py`, `MANIFEST.in`, etc it actually keeps all those files as well
as providing the `pyproject.toml`.   

Next thing is to activate my virtual environment.  Hatch does provide a way to do this by
creating a sub-shell using the below command.  

        hatch shell

### Project Code

Ok for our first step with hatch, lets install our two new app dependencies.  One thing that
is clear is that hatch documentation is a bit more scarse compared to poetry, luckily by running
`hatch --help` I was able to find that `install` will install the packages.  

        hatch install flask requests

So this installed the 2 packages into the virtualenv, however it did not keep record off those
items or the used version in the pyproject.toml.  So after looking over the output (same as a
pip install output) I have the following.  

        Successfully installed Jinja2-2.10 MarkupSafe-1.0 Werkzeug-0.14.1 certifi-2018.8.24 chardet-3.0.4 click-6.7 flask-1.0.2 idna-2.7 itsdangerous-0.24 requests-2.19.1 urllib3-1.23

So looking through the output I need to use `flask==1.0.2` as well as `requests==2.19.1`. Now
that I have the versions, I am not actually sure if I need to place them in the toml files or the
other files and their documentation doesn't say.  So I am going to hope for the best.  For now
lets go ahead and copy over the code pieces.  

        cp ../app.py app.py
        cp ../client.py hatch_app/client.py

Since I don't know where versions are supposed to go, I am going to hope that things work by
just putting the new dependencies in the toml file.  With that done, lets build a package. 

### Creating a Package

To create a package you can use the `build` option on hatch.

        hatch build

This creates two files that it outputs to the `dist` folder.  

        hatch-app-0.0.1.tar.gz
        hatch_app-0.0.1-py3-none-any.whl

Lets create a new consumer project to test how the package works. 

### Package Test

So creating a consumer was pretty straight-forward.  

        mkdir -p hatch-consumer
        cd hatch-consumer
        python3 -m venv .venv
        pip install ../hatch-app/dist/*.whl

I then copied the test.py file.  

        cp ../test.py test.py

After changing the import to use the hatch_app from poetry_app it didn't
work because the dependencies were not there.  

## Filt

So flit looks more like a simple wrapper compared to a full system like poetry
or hatch.  For example, it does not provide the support create a new package
but instead will create a new toml file.  

### Installation

Installation is as easy as the other tools.  

        pip install --user flit

### Project Setup

So we will start by creating our own
package.  

        mkdir flit-app
        cd flit-app
        python3 -m venv .venv
        flit init

When calling `flit init` it asks for a number of parameters that I entered and
it generated this output (toml file).  

        [build-system]
        requires = ["flit"]
        build-backend = "flit.buildapi"

        [tool.flit.metadata]
        module = "flit_app"
        author = "Mike"
        author-email = "miwright@proofpoint.com"
        home-page = "na"

Now lets install our two packages.  Sadly flit does not have a built
in command to do this, so we need to manually add the values to the
toml file ourselves.  

        requires = [
            flit
        ]

however there are no folders, so I need to now create that structure.   

        mkdir -p flit_app
        touch flit_app/__init__.py
        cp ../app.py app.py
        cp ../client.py flit_app/client.py

At this point the install from toml doesn't work... so I am just going to
stop evaluating flit.  

### Project Code

Didn't try

### Creating a Package

Didn't try

### Package Test

Didn't try
