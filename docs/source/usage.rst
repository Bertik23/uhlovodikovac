.. highlight:: python

Usage
=====

To use uhlovodikovac, import it using
::

    import uhlovodikovac

And than setup a variable, that will be your hydrocarbon
::

    hydrocarbon = uhlovodikovac.HydroCarbon("butan")

To draw the image of you hydrocarbon use
::

    hydrocarbon.draw()

If you want to save your image, use
::

    with open("image.png", "wb") as f:
        f.write(hydrocarbon.draw().getbuffer())