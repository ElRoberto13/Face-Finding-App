import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk
import face_recognition
from PIL import Image, ImageTk, ImageDraw
import os.path
class App(tk.Frame):
    """ Creates a frame that contains a button when clicked lets the user to select
    a file and put its filepath into an entry.
    """

    def __init__(self, master, initialdir='', filetypes=()):
        super().__init__(master)
        self.dirpath = tk.StringVar()
        self.photopath = tk.StringVar()
        self._initaldir = initialdir
        self._filetypes = filetypes
        self._oFrame = tk.Frame(self)
        self._oFrame.pack(expand=True)
        self._frame2 = tk.Label(self._oFrame)
        self._canvas = tk.Label(self)
        self.name = tk.StringVar()
        self.create_widgets_one()
        self.create_widgets_two()
        self.create_widgets_three()
        self.display_widgets_one()
        self._counter = 0
    def create_widgets_one(self):
        self.winfo_toplevel().title("gucAI")
        self._frame1 = tk.Frame(self._oFrame)
        self._dirText = tk.Label(self._frame1,text="Directory of pictures:")
        self._dirEntry = tk.Entry(self._frame1, textvariable=self.dirpath)
        self._button = tk.Button(self._frame1, text="Browse...", command=self.browseDir)

        self._next = tk.Button(self, text="Next...",command=self.next)
    def create_widgets_two(self):
        self._frame2 = tk.Frame(self._oFrame)
        self._picText = tk.Label(self._frame2, text="Reference Picture of Face:")
        self._picEntry = tk.Entry(self._frame2, textvariable=self.photopath)
        self._picButton = tk.Button(self._frame2, text="Browse...", command=self.browsePics)
        self._nameText = tk.Label(self._frame2, text = 'Enter Name:')
        self._nameEntry = tk.Entry(self._frame2, textvariable=self.name)
    def create_widgets_three(self):
        self._frame3 = tk.Frame(self._oFrame)
        print('Name: '+self.name.get())
        self._bar = ttk.Progressbar(self._frame3, orient='horizontal', length=200, mode='determinate')
    def next(self):
        if self._counter==0:
            self._counter=1
            self.display_widgets_two()
        elif self._counter == 1:
            self._counter = 2
            self.display_widgets_three()
    def display_widgets_one(self):
        self._frame1.pack()
        self._frame1.pack(anchor = 'center' )
        self._dirText.pack(expand=True,anchor='nw')
        self._dirEntry.pack(fill='x', expand=True)
        self._button.pack(anchor='n')
    def display_widgets_two(self):
        self._frame1.destroy()
        self._frame2.pack(expand=True)
        self._picText.pack(anchor='center')
        self._picEntry.pack(anchor='center')
        self._picButton.pack(anchor='center')
        self._nameText.pack(anchor='w')
        self._nameEntry.pack(anchor='center',expand=True)

    def display_widgets_three(self):
        split = self.dirpath.get().split('/')
        split.pop()
        self.newDir= '/'.join(split)
        self.newDir += '/' + self.name.get()
        if not os.path.exists(self.newDir):
            os.makedirs(self.newDir)
        self._frame2.destroy()
        self._frame3.pack()
        self.trainFace(self.photopath.get())
        faceBox = self.drawBoxOnFace(self.photopath.get())
        faceBox = faceBox.resize((500,500), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(faceBox)
        self.imageLab = tk.Label(self._frame3,image = photo)
        self.imageLab.image = photo
        self._barText = tk.Label(self._frame3, text='Finding pictures of '+self.name.get()+"...")
        self._barText.pack(anchor='w')
        self.imageLab.pack()
        self._bar.pack(anchor='center')
        self.findFaces()
    def browseDir(self):
        self.dirpath.set(fd.askdirectory(initialdir=self._initaldir))
        self._next.pack()
    def browsePics(self):
        self.photopath.set(fd.askopenfilename(initialdir=self._initaldir,filetypes=self._filetypes))
        self._next.pack()
        if len(str(self.photopath.get()))>0:
            image = Image.open(str(self.photopath.get()))
            image = image.resize((500,500), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(image)
            self._canvas.pack_forget()
            self._canvas = tk.Label(self._frame2, image=photo)
            self._canvas.image = photo
            self._canvas.pack(anchor='center')
    def trainFace(self,face):
        face_image = face_recognition.load_image_file(face)
        face_encoding = face_recognition.face_encodings(face_image)[0]
        self.known_face_encodings = [
            face_encoding
        ]
        self.known_face_names = [
            self.name.get()
        ]
    def drawBoxOnFace(self,face):
        unknown_image = face_recognition.load_image_file(face)
        # Find all the faces and face encodings in the unknown image
        face_locations = face_recognition.face_locations(unknown_image)
        face_encodings = face_recognition.face_encodings(unknown_image, face_locations)
        pil_image = Image.fromarray(unknown_image)
        # Create a Pillow ImageDraw Draw instance to draw with
        draw = ImageDraw.Draw(pil_image)
        # Loop through each face found in the unknown image
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"
            # If a match was found in known_face_encodings, just use the first one.
            if True in matches:
                first_match_index = matches.index(True)
                name = self.known_face_names[first_match_index]
            # Draw a box around the face using the Pillow module
            draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))

            # Draw a label with a name below the face
            text_width, text_height = draw.textsize(name)
            draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
            draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))
        return pil_image
    def findFaces(self):
        total = len([name for name in os.listdir(self.dirpath.get()) if os.path.isfile(os.path.join(self.dirpath.get(), name))])
        count = 0.0
        for filename in os.listdir(self.dirpath.get()):
            if os.path.isfile(os.path.join(self.dirpath.get(),filename)):
                count += 1
            if filename.endswith(".jpg") or filename.endswith(".png"):
                unknown_image = face_recognition.load_image_file(self.dirpath.get()+'/'+filename)
                # Find all the faces and face encodings in the unknown image
                face_locations = face_recognition.face_locations(unknown_image)
                face_encodings = face_recognition.face_encodings(unknown_image, face_locations)

                # Convert the image to a PIL-format image so that we can draw on top of it with the Pillow library
                # See http://pillow.readthedocs.io/ for more about PIL/Pillow
                image = Image.fromarray(unknown_image)
                orginal = image.copy()
                # Create a Pillow ImageDraw Draw instance to draw with
                draw = ImageDraw.Draw(image)
                found = False;
                # Loop through each face found in the unknown image
                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)

                    name = "Unknown"

                    # If a match was found in known_face_encodings, just use the first one.
                    if True in matches:
                        first_match_index = matches.index(True)
                        name = self.known_face_names[first_match_index]
                        if name == self.name.get():
                            found = True;
                    # Draw a box around the face using the Pillow module
                    draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))

                    # Draw a label with a name below the face
                    text_width, text_height = draw.textsize(name)
                    draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255),
                                   outline=(0, 0, 255))
                    draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))

                # Remove the drawing library from memory as per the Pillow docs

                # Display the resulting image
                # pil_image.show()

                # You can also save a copy of the new image to disk if you want by uncommenting this line
                if found:
                    orginal.save(self.newDir+'/'+filename)
                    image = image.resize((500, 500), Image.ANTIALIAS)
                    photo = ImageTk.PhotoImage(image)
                    self.imageLab.configure(image=photo)
                    self.imageLab.image = photo
                    print('found')
                self._bar['value'] = count / total * 100
                self.update_idletasks()
        del draw
# self._p = ttk.Progressbar(self._frame, orient='horizontal', length=200, mode='determinate')
# self._p.pack()
# self._p.start(interval=5)
# dir = str(self.dirpath.get())
# print(len([name for name in os.listdir(dir) if os.path.isfile(os.path.join(dir, name))]))
if __name__ == '__main__':
    root = tk.Tk()

    file_browser = App(root, initialdir=r"C:\Users",
                                filetypes=(('Portable Network Graphics','*.png'),('JPEG','*.jpg'),
                                                            ("All files", "*.*")))
    file_browser.pack(fill='x', expand=True)

    root.mainloop()