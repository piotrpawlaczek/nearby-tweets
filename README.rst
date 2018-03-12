.. image:: https://user-images.githubusercontent.com/4227868/36950421-f0698904-1ff5-11e8-8804-2a447ebeaf3d.png


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
    $ open http://localhost:8000/?w=-122.75,36.8,-121.75,37.8
    $ open http://localhost:8000/map/?w=-122.75,36.8,-121.75,37.8  # live tracking on map


Test
====
Run unittests:

.. code-block:: shell

    $ pytest
