def list_widgets(widget, indent=0):
    """ Rekurzívan kiírja a widget fát """
    print(" " * indent + f"{widget.__class__.__name__}: {widget}")
    for child in widget.children:
        list_widgets(child, indent + 2)
