import os
import platform
import subprocess
import tkinter as tkr
from datetime import datetime
from pathlib import Path
from tkinter import filedialog as fd, messagebox
from work_divider.assign_workers import generate_work_sheet


# TODO: it should remember some from the last time app was invoked
# TODO: add tests


class GUI:
    def __init__(self) -> None:
        self.root = tkr.Tk()
        self.root.geometry("500x500")
        self.root.title("Midan's Sheet Processor")

        self._table_path = "Table path not set!"
        self._tablebase_path = "Tablebase path not set!"

        self._output_name = f"output_{datetime.now().date()}.xlsx"
        self._output_folder = Path(".").absolute()

        x_coord, y_coord, y_coef = 0.05, 0.1, 0.05

        # Button to select table file
        self.table_button = tkr.Button(
            self.root,
            text="Select table file",
            command=self.select_table,
            justify="center",
        )
        self.table_button.place(
            relx=x_coord,
            rely=y_coord,
            anchor="w",
        )

        # Label indicating which table file has been selected
        self.table_path_label = tkr.Label(
            self.root,
            text=self._table_path,
            justify="left",
        )
        y_coord += y_coef
        self.table_path_label.place(
            relx=x_coord,
            rely=y_coord,
            anchor="w",
        )

        # Button to select tablebase file
        self.tablebase_button = tkr.Button(
            self.root,
            text="Select tablebase file",
            command=self.select_tablebase,
            justify="center",
        )
        y_coord += y_coef
        self.tablebase_button.place(
            relx=x_coord,
            rely=y_coord,
            anchor="w",
        )

        # Label indicating which tablebase file has been selected
        self.tablebase_path_label = tkr.Label(
            self.root,
            text=self._tablebase_path,
            justify="left",
        )
        y_coord += y_coef
        self.tablebase_path_label.place(
            relx=x_coord,
            rely=y_coord,
            anchor="w",
        )

        # Button to select output folder
        self.output_folder_button = tkr.Button(
            self.root,
            text="Select output folder",
            command=self.select_output_folder,
            justify="center",
        )
        y_coord += y_coef
        self.output_folder_button.place(
            relx=x_coord,
            rely=y_coord,
            anchor="w",
        )

        # Button to set output file name
        self.output_name_button = tkr.Button(
            self.root,
            text="Set output file name",
            command=self.set_output_name,
            justify="center",
        )
        self.output_name_button.place(
            relx=1 - x_coord,
            rely=y_coord,
            anchor="e",
        )

        # Label indicating output name
        self.output_name_label = tkr.Label(
            self.root,
            text=self._output_name,
        )
        y_coord += y_coef
        self.output_name_label.place(
            relx=1 - x_coord,
            rely=y_coord,
            anchor="e",
        )

        # Label indicating output folder
        self.output_folder_label = tkr.Label(
            self.root,
            text=str(self._output_folder.absolute()),
            justify="left",
        )
        self.output_folder_label.place(
            relx=x_coord,
            rely=y_coord,
            anchor="w",
        )

        # Button to generate outoput
        self.generate_output_button = tkr.Button(
            self.root,
            text="Generate output",
            command=self.generate_output,
            justify="center",
        )
        self.generate_output_button.place(
            relx=0.5,
            rely=0.5,
            anchor=tkr.CENTER,
        )

        self.set_output_widgets()

        self.root.mainloop()

    def select_table(self) -> None:
        new_path = Path(
            fd.askopenfilename(
                initialdir=".",
                title="Select a .xlsx table file",
                filetypes=(("xlsx files", "*.xlsx"),),
            )
        ).absolute()

        if new_path.is_file():
            # Set table path
            self._table_path = str(new_path)

            # Update table path label
            self.table_path_label.config(text=self._table_path)

    def select_tablebase(self) -> None:
        new_path = Path(
            fd.askopenfilename(
                initialdir=".",
                title="Select a .xlsx tablebase file",
                filetypes=(("xlsx files", "*.xlsx"),),
            )
        ).absolute()

        if new_path.is_file():
            # Set table path
            self._tablebase_path = str(new_path)

            # Update table path label
            self.tablebase_path_label.config(text=self._tablebase_path)

    def select_output_folder(self) -> None:
        self._output_folder = Path(
            fd.askdirectory(
                initialdir=".",
                title="Select output folder",
            )
        ).absolute()

    def set_output_name(self) -> None:
        output_name = tkr.simpledialog.askstring(
            # self.root,
            title="Text Prompt",
            prompt="Set output file name",
            initialvalue=self._output_name,
        )

        if not output_name.endswith(".xlsx"):
            output_name += ".xlsx"

        self._output_name = output_name

        self.output_name_label.config(text=self._output_name)

    @property
    def output_path(self) -> Path:
        return (self._output_folder / self._output_name).absolute()

    def generate_output(self):
        if self.output_path.is_file():
            answer = messagebox.askquestion(
                title="File already exists",
                message="File already exists!\nDo you want to overwrite it?",
                default="yes",
                type="yesno",
            )

            if answer == "no":
                return

        try:
            generate_work_sheet(
                data_path=self._table_path,
                tablebase_path=self._tablebase_path,
                output_path=self.output_path,
            )
        except FileNotFoundError:
            # Pop up error dialog
            messagebox.showerror(
                title="FileNotFoundError",
                message="Set correct table and tablebase paths!",
            )
        except Exception as e:
            # Pop up error dialog
            messagebox.showerror(
                title="Error",
                message=str(e),
            )
        finally:
            # if file is generated, add a button to open it
            if self.output_path.is_file():
                self.set_output_widgets()

    def set_output_widgets(self):
        self.generated_label = tkr.Label(
            self.root,
            text=f"Output file generated to {self.output_path.absolute()}!",
        )
        self.open_button = tkr.Button(
            self.root, text="Open output", command=self.open_output
        )

        self.generated_label.place(relx=0.5, rely=0.6, anchor=tkr.CENTER)
        self.open_button.place(relx=0.5, rely=0.7, anchor=tkr.CENTER)

    def open_output(self):
        open_file(self.output_path)


def open_file(filepath: Path | str) -> None:
    if platform.system() == "Darwin":  # macOS
        subprocess.call(("open", filepath))
    elif platform.system() == "Windows":  # Windows
        os.startfile(filepath)
    else:  # linux
        subprocess.call(("xdg-open", filepath))


if __name__ == "__main__":
    GUI()
