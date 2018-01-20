=============
 Soundground
=============

Native Soundcloud client built on Python and curses

(Still a work in progress. Check back soon!)

Running Soundground
-------------------

.. code:: bash

    # Clone repo
    git clone git@github.com:bspst/soundground.git
    cd soundground

    # Install requirements
    sudo apt-get install -y vlc
    pip install -r requirements.txt
    python ./setup.py install

    # Run soundground
    python soundground

Using Soundground
-----------------

.. image:: https://raw.githubusercontent.com/bspst/soundground/master/docs/source/_static/images/soundground_ui.png

Controls:

- :kbd:`j`/:kbd:`k` to navigate through the list
- :kbd:`Tab` to cycle through lists (navigation or playlist)
- :kbd:`Enter` to activate highlighted list item
