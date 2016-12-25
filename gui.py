#!/usr/bin/python3

import PIL.Image
import PIL.ImageTk
import tkinter as tk


class _Context(tk.Text):
    CONTEXT_COUNT = 3  # Lines to display before/after the current one
    # TODO: What about files with over 10,000 lines?
    LINE_NUMBER_WIDTH = 5  # Number of characters to allocate for line numbers

    def __init__(self, tk_parent, data, axis):
        height = 1 + 2 * self.CONTEXT_COUNT
        # TODO: Configurable width for files with long lines
        width = 80 + 2 + self.LINE_NUMBER_WIDTH
        # TODO: Is the font name really stringly typed? (Maybe yes)
        super().__init__(tk_parent, width=width, height=height,
                state=tk.DISABLED, font="TkFixedFont")
        # TODO: Use a NamedTuple?
        self._tokens, self._lines, self._boundaries = data
        self._line_numbers = [boundary[0][0] for boundary in self._boundaries]
        self.pack()
        self._axis = axis

    def display(self, event):
        # TODO: Check this whole thing for off-by-one errors.
        pixel_index = getattr(event, self._axis)
        #print("index {} of {}".format(pixel_index, len(self._line_numbers)))
        if not (0 <= pixel_index < len(self._line_numbers)):
            print("Out of range; skipping!")
            return
        line_number = self._line_numbers[pixel_index]
        start = line_number - self.CONTEXT_COUNT
        end   = line_number + self.CONTEXT_COUNT + 1
        # Recall that line_number comes from the token module, which starts
        # counting at 1 instead of 0.
        # TODO: Change the 5 to a LINE_NUMBER_WIDTH
        text = "\n".join("{:>5}: {}".format(i, self._lines[i - 1])
                           if 0 < i <= len(self._lines) else ""
                           for i in range(start, end))
        # Update the displayed code
        self.configure(state=tk.NORMAL)
        self.delete("1.0", tk.END)
        self.insert(tk.INSERT, text)
        # Highlight the token of interest.
        (a1, a2), (b1, b2) = self._boundaries[pixel_index]
        self.tag_add("token",
                     "{}.{}".format(self.CONTEXT_COUNT + 1,
                                    a2 + self.LINE_NUMBER_WIDTH + 2),
                     "{}.{}".format(self.CONTEXT_COUNT + 1 + b1 - a1,
                                    b2 + self.LINE_NUMBER_WIDTH + 2))
        self.tag_config("token", background="yellow")
        # Remember to disable editing again when we're done!
        self.configure(state=tk.DISABLED)


class _Gui(tk.Frame):
    def __init__(self, matrix, data_a, data_b, root):
        super().__init__(root)
        self.pack(fill=tk.BOTH, expand="true")
        # Store the image as a member variable to keep it from going out of
        # scope.
        # TODO: Deal with overly large matrices, likely by allowing panning and
        # zooming with the mouse.
        image = PIL.Image.fromarray(matrix * 255)
        self._image = PIL.ImageTk.PhotoImage(image)
        self._map = tk.Label(self, image=self._image)
        self._map.pack()
        self._map.bind("<Motion>", self._on_motion)
        self._map.bind("<Enter>",  self._on_motion)

        # We're using (row, col) format, so the first one changes with Y.
        self._contexts = [_Context(self, data, axis)
                          for data, axis in ((data_a, "y"), (data_b, "x"))]

    def _on_motion(self, event):
        [context.display(event) for context in self._contexts]


def launch(matrix, data_a, data_b):
    root = tk.Tk()

    def _quit(event):
        root.destroy()
    [root.bind("<Control-{}>".format(char), _quit) for char in "wWqQ"]

    gui = _Gui(matrix, data_a, data_b, root)
    root.mainloop()
