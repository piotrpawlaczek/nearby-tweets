Nearby tweets
==============

Following and visualizing nearby tweets.

Utilizes some cool python 3.6+ features:

- typing
- asyncio
- f'strings
- websockets & push notifications

No twitter API auth or configuration required.
Fast and async web server, realtime data on a map.

Installation
============

Python 3.6+ is supported only.

.. code-block:: shell

    $ pipenv install .


Usage
=====

.. code-block:: shell

    $ python run.py
    $ open http://localhost:8000/  # basic ui
    $ open http://localhost:8000/?w=Londodn  # get tweets from London location
    $ open http://localhost:8000/?w=geocode:52.2,21.0&l=en  # tell app to use coordinates and english lang
    $ open http://localhost:8000/map/?w=53.3498050,-6.2603100  # live tracking on map


Test
====
Run unittests:

.. code-block:: shell

    $ pytest
