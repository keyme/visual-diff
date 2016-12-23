#!/usr/bin/python3

import PIL.Image
import PIL.ImageTk
import tkinter as tk


class Context:
    CONTEXT_COUNT = 3  # Number of lines before and after to show

    def __init__(self, tk_super, data, axis):
        # TODO: Use a NamedTuple?
        self._tokens, self._lines, self._line_numbers = data
        # Pad the lines so the context displays properly at the beginning and
        # end of the file.
        self._lines = ([""] * self.CONTEXT_COUNT + self._lines +
                       [""] * self.CONTEXT_COUNT)
        height = 1 + 2 * self.CONTEXT_COUNT
        # TODO: Use a fixed-width font.
        self._tk_label = tk.Label(tk_super, text="", width=80, height=height,
                justify="left")
        self._tk_label.pack(side="top")
        """
        # TODO: Figure out the width of the line numbers section, and make it
        # correct across files of vastly different size.
        self.tk_line_numbers = tk.Label(self._tk_label, text="", width=6,
                height=height, justify="right")
        self._tk_label.pack(side="left")
        """
        self._axis = axis

    def on_motion(self, event):
        # TODO: Check this whole thing for off-by-one errors.
        pixel_index = getattr(event, self._axis)
        if not (0 <= pixel_index < len(self._line_numbers)):
            print("Out of range; skipping!")
            return
        line_number = self._line_numbers[pixel_index]
        #line_number += self.CONTEXT_COUNT  # Due to the padding at the start
        # Recall that line_number comes from the token module, which starts
        # counting at 1 instead of 0.
        start = line_number - self.CONTEXT_COUNT - 1
        end   = line_number + self.CONTEXT_COUNT
        # Remember to offset by the padding.
        lines = self._lines[start + self.CONTEXT_COUNT:
                            end   + self.CONTEXT_COUNT]
        line_numbers = range(start, end)
        # TODO: Highlight the token of interest?
        self._tk_label.configure(text="\n".join(lines))
        line_numbers = [
                "{}:".format(i) if 1 <= i <= len(self._lines) else ""
                for i in line_numbers]
        line_numbers = "\n".join(line_numbers)
        print(line_numbers)
        """
        self._tk_line_numbers.configure(text=line_numbers)
        """

    def on_leave(self, event):
        self._tk_label.configure(text="")
        #self._tk_line_numbers.configure(text="")


# TODO: Why does this inherit from tk.Frame? Shouldn't it encapsulate a Frame
# instead?
class Gui(tk.Frame):
    def __init__(self, matrix, data_a, data_b, root):
        # TODO: super().__init__(self, root) doesn't work. Why?
        tk.Frame.__init__(self, root)
        # Store the image as a member variable to keep it from going out of
        # scope.
        image = PIL.Image.fromarray(matrix * 255)
        self._image = PIL.ImageTk.PhotoImage(image)
        self._map = tk.Label(self, image=self._image)
        self._map.pack(side="top")
        self._map.bind("<Leave>", self.on_leave)
        self._map.bind("<Motion>", self.on_motion)

        # We're using (row, col) format, so the first one changes with Y.
        self._contexts = [Context(self, data, axis)
                          for data, axis in ((data_a, "y"), (data_b, "x"))]

    def on_leave(self, event):
        [context.on_leave(event) for context in self._contexts]

    def on_motion(self, event):
        [context.on_motion(event) for context in self._contexts]


def launch(matrix, data_a, data_b):
    root = tk.Tk()
    gui = Gui(matrix, data_a, data_b, root)
    gui.pack(side="top", fill="both", expand="true")
    root.mainloop()


if __name__ == "__main__":
    launch(1,2,3)
