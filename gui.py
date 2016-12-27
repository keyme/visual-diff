#!/usr/bin/python3

import functools
import tkinter as tk

from zoom_map import ZoomMap


class _Context(tk.Text):
    CONTEXT_COUNT = 3  # Lines to display before/after the current one
    # TODO: What about files with over 10,000 lines?
    LINE_NUMBER_WIDTH = 5  # Number of characters to allocate for line numbers
    PRELUDE_WIDTH = LINE_NUMBER_WIDTH + 2  # Line number, colon, space
    # TODO: What about files with very long lines? They currently wrap around to
    # the next line and push later context out of the widget. Should we truncate
    # them instead? and if so, should we change which part gets cut based on the
    # location of the token within the line?
    TEXT_WIDTH = 80

    def __init__(self, tk_parent, data, axis, zoom_map):
        # TODO: integrate the zoom map into this.
        height = 1 + 2 * self.CONTEXT_COUNT
        # We insert a colon and space between the line number and text.
        width = self.PRELUDE_WIDTH + self.TEXT_WIDTH
        super().__init__(tk_parent, width=width, height=height,
                state=tk.DISABLED, font="TkFixedFont")
        # TODO: Use a NamedTuple?
        self._tokens, self._lines, self._boundaries = data
        self.pack()
        self._axis = axis
        self._zoom_map = zoom_map

    def display(self, event):
        # TODO: Check this whole thing for off-by-one errors.
        # The zoom level is equivalent to the number of tokens described by the
        # current pixel in the map.
        zoom_level = self._zoom_map.zoom_level()
        begin_token_index = getattr(event, self._axis) * zoom_level
        end_token_index = min(begin_token_index + zoom_level,
                              len(self._boundaries)) - 1
        if not (0 <= begin_token_index < len(self._boundaries)):
            print("Out of range; skipping!")
            return
        line_number = self._boundaries[begin_token_index][0][0]
        # Recall that line_number comes from the token module, which starts
        # counting at 1 instead of 0.
        start = line_number - self.CONTEXT_COUNT - 1
        end   = line_number + self.CONTEXT_COUNT
        lines = ["{:>{}}: {}".format(i + 1, self.LINE_NUMBER_WIDTH,
                                     self._lines[i])
                 if 0 <= i < len(self._lines) else ""
                 for i in range(start, end)]
        text = "\n".join(lines)
        # Update the displayed code
        self.configure(state=tk.NORMAL)
        self.delete("1.0", tk.END)
        self.insert(tk.INSERT, text)
        # Highlight the tokens of interest.
        (a1, a2) = self._boundaries[begin_token_index][0]
        (b1, b2) = self._boundaries[end_token_index][1]
        self.tag_add("token",
                     "{}.{}".format(self.CONTEXT_COUNT + 1,
                                    a2 + self.PRELUDE_WIDTH),
                     "{}.{}".format(self.CONTEXT_COUNT + 1 + b1 - a1,
                                    b2 + self.PRELUDE_WIDTH))
        self.tag_config("token", background="yellow")
        # ...but don't highlight the line numbers on multi-line tokens.
        for i in range(self.CONTEXT_COUNT):
            line = i + self.CONTEXT_COUNT + 2
            self.tag_remove("token",
                            "{}.{}".format(line, 0),
                            "{}.{}".format(line, self.PRELUDE_WIDTH))
        # Remember to disable editing again when we're done!
        self.configure(state=tk.DISABLED)


class _Map(tk.Label):
    def __init__(self, zoom_map, tk_parent):
        # TODO: Deal with overly large matrices, by allowing panning with the
        # mouse and making this widget a constant size.
        # TODO: This class has very little in it. It should probably be rolled
        # into something else, but I don't know if it should be rolled into the
        # ZoomMap or _Gui classes.
        self._zoom_map = zoom_map
        super().__init__(tk_parent, image=self._zoom_map.image())
        self.pack()
        self.bind("<Button-4>",   functools.partial(self._zoom,  1))
        self.bind("<Button-5>",   functools.partial(self._zoom, -1))
        self.bind("<Motion>",     tk_parent.on_motion)
        self.bind("<Enter>",      tk_parent.on_motion)

    def _zoom(self, amount, event):
        self._zoom_map.zoom(amount)
        self.configure(image=self._zoom_map.image())


class _Gui(tk.Frame):
    def __init__(self, matrix, data_a, data_b, root):
        super().__init__(root)
        self.pack(fill=tk.BOTH, expand="true")
        zoom_map = ZoomMap(matrix)
        self._map = _Map(zoom_map, self)

        # We're using (row, col) format, so the first one changes with Y.
        self._contexts = [_Context(self, data, axis, zoom_map)
                          for data, axis in ((data_a, "y"), (data_b, "x"))]

    def on_motion(self, event):
        [context.display(event) for context in self._contexts]


def launch(matrix, data_a, data_b):
    root = tk.Tk()

    def _quit(event):
        root.destroy()
    [root.bind("<Control-{}>".format(char), _quit) for char in "wWqQ"]

    gui = _Gui(matrix, data_a, data_b, root)
    root.mainloop()
