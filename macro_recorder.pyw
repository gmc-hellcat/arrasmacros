#if you cant tell already, this is a pythonw file you will need to install the following modules. 
#use command prompt with or without admin permissions to run
#pip install pynput
#pip install pyperclip
#pip install pystray
#check installs with 
#pip list
#don't bother if you are not on windows




from pynput import mouse, keyboard
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
import pyperclip
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import sys
import os
import time
import threading
import pystray
from PIL import Image, ImageDraw

class MacroRecorder:
    def __init__(self):
        # Single instance check
        self.lock_file = os.path.join(os.path.expanduser("~"), ".macro_recorder.lock")
        if os.path.exists(self.lock_file):
            try:
                with open(self.lock_file, 'r') as f:
                    pid = int(f.read().strip())
                # Check if process is still running
                if sys.platform == "win32":
                    import ctypes
                    kernel32 = ctypes.windll.kernel32
                    PROCESS_QUERY_INFORMATION = 0x0400
                    handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, 0, pid)
                    if handle:
                        kernel32.CloseHandle(handle)
                        messagebox.showerror("Already Running", "Macro Recorder is already running!")
                        sys.exit(1)
                else:
                    try:
                        os.kill(pid, 0)
                        messagebox.showerror("Already Running", "Macro Recorder is already running!")
                        sys.exit(1)
                    except OSError:
                        pass
            except:
                pass
        
        # Write current PID to lock file
        with open(self.lock_file, 'w') as f:
            f.write(str(os.getpid()))
        
        self.recording = False
        self.mouse_positions = []
        
        # Controllers
        self.mouse_controller = MouseController()
        self.keyboard_controller = KeyboardController()
        
        # Macro actions
        self.start_actions = []  # Actions at the very start
        self.end_actions = []  # Actions at the very end
        
        # Create UI window
        self.root = tk.Tk()
        self.root.title("Advanced Macro Recorder")
        self.root.geometry("650x680")
        self.root.configure(bg='#ffffff')
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        
        self.setup_ui()
        self.tray_icon = None
        self.create_tray_icon()
        
    def setup_ui(self):
        """Setup the UI"""
        # Main container
        self.main_frame = tk.Frame(self.root, bg='#ffffff', padx=16, pady=16)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title and Status
        header_frame = tk.Frame(self.main_frame, bg='#ffffff')
        header_frame.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(header_frame, text="Macro Recorder", 
                font=('Segoe UI', 18, 'bold'), bg='#ffffff', fg='#1a1a1a').pack(side=tk.LEFT)
        
        self.status_label = tk.Label(header_frame, text="Ready", 
                                     font=('Segoe UI', 10), bg='#ffffff', fg='#6b7280')
        self.status_label.pack(side=tk.RIGHT)
        
        # Hotkeys info
        hotkeys_frame = tk.Frame(self.main_frame, bg='#f8f9fa', relief=tk.FLAT, bd=0)
        hotkeys_frame.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(hotkeys_frame, text="Hotkeys", font=('Segoe UI', 9, 'bold'), 
                bg='#f8f9fa', fg='#1a1a1a').pack(anchor='w', padx=12, pady=(10, 6))
        
        hotkeys = [
            ("F1", "Start/Stop recording mouse positions"),
            ("R", "Record current mouse position"),
            ("F2", "Copy positions to clipboard"),
            ("F3", "Open Action Editor"),
            ("F4", "Run Macro"),
            ("ESC", "Exit")
        ]
        
        for key, desc in hotkeys:
            row = tk.Frame(hotkeys_frame, bg='#f8f9fa')
            row.pack(fill=tk.X, padx=12, pady=2)
            tk.Label(row, text=key, font=('Consolas', 8, 'bold'), 
                    bg='#e5e7eb', fg='#374151', width=5, relief=tk.FLAT, padx=6, pady=2).pack(side=tk.LEFT, padx=(0, 10))
            tk.Label(row, text=desc, font=('Segoe UI', 9), 
                    bg='#f8f9fa', fg='#4b5563', anchor='w').pack(side=tk.LEFT)
        
        tk.Label(hotkeys_frame, text=" ", bg='#f8f9fa', height=1).pack()
        
        # Mouse positions list
        tk.Label(self.main_frame, text="Recorded Mouse Positions", 
                font=('Segoe UI', 10, 'bold'), bg='#ffffff', fg='#1a1a1a').pack(anchor='w', pady=(0, 6))
        
        list_frame = tk.Frame(self.main_frame, bg='#f8f9fa', relief=tk.FLAT, bd=0)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.positions_listbox = tk.Listbox(list_frame, font=('Consolas', 9), 
                                         bg='#ffffff', fg='#1f2937', 
                                         yscrollcommand=scrollbar.set,
                                         relief=tk.FLAT, bd=0, highlightthickness=1,
                                         highlightbackground='#e5e7eb', highlightcolor='#3b82f6',
                                         selectmode=tk.EXTENDED, selectbackground='#dbeafe', selectforeground='#1e40af')
        self.positions_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)
        scrollbar.config(command=self.positions_listbox.yview)
        
        # Count label
        self.count_label = tk.Label(self.main_frame, text="0 positions", 
                                   font=('Segoe UI', 9), bg='#ffffff', fg='#9ca3af')
        self.count_label.pack(pady=(8, 0))
        # Edit position actions button
        btn_row = tk.Frame(self.main_frame, bg='#ffffff')
        btn_row.pack(pady=4)
        
        tk.Button(btn_row, text="Edit Actions", 
                  command=self.edit_position_actions,
                  bg='#3b82f6', fg='white', font=('Segoe UI', 9),
                  relief=tk.FLAT, padx=12, pady=7, cursor='hand2').pack(side=tk.LEFT, padx=3)
        
        tk.Button(btn_row, text="Add Comment", 
                  command=self.add_comment,
                  bg='#3b82f6', fg='white', font=('Segoe UI', 9),
                  relief=tk.FLAT, padx=12, pady=7, cursor='hand2').pack(side=tk.LEFT, padx=3)
        
        # Edit/Delete/Add position buttons
        edit_row = tk.Frame(self.main_frame, bg='#ffffff')
        edit_row.pack(pady=4)
        
        tk.Button(edit_row, text="Edit Coordinates", 
                  command=self.edit_coordinates,
                  bg='#6b7280', fg='white', font=('Segoe UI', 9),
                  relief=tk.FLAT, padx=12, pady=7, cursor='hand2').pack(side=tk.LEFT, padx=3)
        
        tk.Button(edit_row, text="Delete", 
                  command=self.delete_positions,
                  bg='#ef4444', fg='white', font=('Segoe UI', 9),
                  relief=tk.FLAT, padx=12, pady=7, cursor='hand2').pack(side=tk.LEFT, padx=3)
        
        tk.Button(edit_row, text="Add Position", 
                  command=self.add_new_position,
                  bg='#10b981', fg='white', font=('Segoe UI', 9),
                  relief=tk.FLAT, padx=12, pady=7, cursor='hand2').pack(side=tk.LEFT, padx=3)
        
        # Save/Load buttons
        save_load_row = tk.Frame(self.main_frame, bg='#ffffff')
        save_load_row.pack(pady=4)
        
        tk.Button(save_load_row, text="💾 Save Macro", 
                  command=self.save_macro,
                  bg='#6b7280', fg='white', font=('Segoe UI', 9),
                  relief=tk.FLAT, padx=12, pady=7, cursor='hand2').pack(side=tk.LEFT, padx=3)
        
        tk.Button(save_load_row, text="📁 Load Macro", 
                  command=self.load_macro,
                  bg='#6b7280', fg='white', font=('Segoe UI', 9),
                  relief=tk.FLAT, padx=12, pady=7, cursor='hand2').pack(side=tk.LEFT, padx=3)
        
        # Actions summary
        self.actions_summary = tk.Label(self.main_frame, 
                                       text="No actions configured (Press F3 to configure)",
                                       font=('Segoe UI', 9, 'italic'), bg='#ffffff', fg='#9ca3af')
        self.actions_summary.pack(pady=(6, 0))
    
    def create_tray_icon(self):
        """Create system tray icon"""
        image = Image.new('RGB', (64, 64), color='blue')
        draw = ImageDraw.Draw(image)
        draw.rectangle([16, 16, 48, 48], fill='white')
        
        menu = pystray.Menu(
            pystray.MenuItem("Show Window", self.show_window),
            pystray.MenuItem("Record Position (R)", self.record_position),
            pystray.MenuItem("Copy Positions (F2)", self.copy_to_clipboard),
            pystray.MenuItem("Action Editor (F3)", self.open_editor),
            pystray.MenuItem("Run Macro (F4)", self.run_macro),
            pystray.MenuItem("Start/Stop Recording (F1)", self.toggle_recording),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Save Macro", self.save_macro),
            pystray.MenuItem("Load Macro", self.load_macro),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self.quit_app)
        )
        
        self.tray_icon = pystray.Icon("macro_recorder", image, "Macro Recorder", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
    
    def hide_window(self):
        """Hide window to tray"""
        self.root.withdraw()
    
    def show_window(self):
        """Show window from tray"""
        self.root.after(0, self.root.deiconify)
    
    def quit_app(self):
        """Quit application"""
        try:
            if os.path.exists(self.lock_file):
                os.remove(self.lock_file)
        except:
            pass
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()
        
    def update_actions_summary(self):
        """Update the actions summary label"""
        summary_parts = []
        if self.start_actions:
            summary_parts.append(f"Start: {len(self.start_actions)} actions")
        if self.end_actions:
            summary_parts.append(f"End: {len(self.end_actions)} actions")
        
        if summary_parts:
            self.actions_summary.config(text=" | ".join(summary_parts))
        else:
            self.actions_summary.config(text="No actions configured (Press F3 to configure)")
    def open_editor(self):
        """Open the action editor window"""
        self.root.after(0, lambda: ActionEditor(self.root, self.start_actions, 
                             self.end_actions, self.on_editor_save))
    def on_editor_save(self, start, end):
        """Callback when editor saves changes"""
        self.start_actions = start
        self.end_actions = end
        self.update_actions_summary()
        
    def update_ui(self):
        """Update UI elements"""
        if self.recording:
            self.status_label.config(text="Recording...", fg='#ef4444')
        else:
            self.status_label.config(text="Ready", fg='#6b7280')
        
        self.count_label.config(text=f"{len(self.mouse_positions)} positions")
        
    def on_press(self, key):
        """Handle key press events"""
        try:
            if key == Key.f1:
                self.toggle_recording()
            elif hasattr(key, 'char') and key.char == 'r':
                self.record_position()
            elif key == Key.f2:
                self.copy_to_clipboard()
            elif key == Key.f3:
                self.open_editor()
            elif key == Key.f4:
                self.run_macro()
            elif key == Key.esc:
                self.quit_app()
                return False
        except AttributeError:
            pass
    
    def toggle_recording(self):
        """Toggle recording mode"""
        if not self.recording:
            self.recording = True
            self.mouse_positions = []
            self.positions_listbox.delete(0, tk.END)
        else:
            self.recording = False
        
        self.update_ui()
    
    def record_position(self):
        """Record current mouse position"""
        if self.recording:
            x, y = self.mouse_controller.position
            self.mouse_positions.append({'x': x, 'y': y, 'actions': [], 'comment': ''})
            
            index = len(self.mouse_positions)
            self.positions_listbox.insert(tk.END, f"{index}. Position ({x}, {y}) - 0 actions")
            self.positions_listbox.see(tk.END)
            self.update_ui()
    
    def copy_to_clipboard(self):
        """Copy positions to clipboard"""
        if len(self.mouse_positions) == 0:
            self.status_label.config(text="No positions to copy", fg='#f59e0b')
            self.root.after(2000, lambda: self.update_ui())
            return
        
        output = "Recorded Mouse Positions:\n\n"
        for i, pos_data in enumerate(self.mouse_positions, 1):
            comment_str = f" - {pos_data.get('comment', '')}" if pos_data.get('comment') else ""
            output += f"{i}. ({pos_data['x']}, {pos_data['y']}) - {len(pos_data['actions'])} actions{comment_str}\n"
        
        pyperclip.copy(output)
        self.status_label.config(text="Copied to clipboard", fg='#10b981')
        self.root.after(2000, lambda: self.update_ui())
    def edit_position_actions(self):
        """Edit actions for selected position(s)"""
        selections = self.positions_listbox.curselection()
        if not selections:
            messagebox.showinfo("Edit", "Select position(s) first")
            return
        
        if len(selections) == 1:
            # Single selection - edit normally
            index = selections[0]
            pos_data = self.mouse_positions[index]
            
            def update_callback(actions):
                pos_data['actions'] = actions
                # Update display
                comment_str = f" - {pos_data['comment']}" if pos_data['comment'] else ""
                self.positions_listbox.delete(index)
                self.positions_listbox.insert(index, 
                    f"{index+1}. Position ({pos_data['x']}, {pos_data['y']}) - {len(actions)} actions{comment_str}")
            
            PositionActionEditor(self.root, pos_data['actions'], update_callback, index+1)
        else:
            # Multiple selections - apply same actions to all
            def update_callback(actions):
                for index in selections:
                    self.mouse_positions[index]['actions'] = actions.copy()
                    pos_data = self.mouse_positions[index]
                    comment_str = f" - {pos_data['comment']}" if pos_data['comment'] else ""
                    self.positions_listbox.delete(index)
                    self.positions_listbox.insert(index, 
                        f"{index+1}. Position ({pos_data['x']}, {pos_data['y']}) - {len(actions)} actions{comment_str}")
            
            PositionActionEditor(self.root, [], update_callback, f"{len(selections)} positions")
    
    def add_comment(self):
        """Add comment to selected position(s)"""
        selections = self.positions_listbox.curselection()
        if not selections:
            messagebox.showinfo("Add Comment", "Select position(s) first")
            return
        
        # Prompt for comment
        comment_window = tk.Toplevel(self.root)
        comment_window.title("Add Comment")
        comment_window.geometry("400x150")
        comment_window.configure(bg='#ffffff')
        comment_window.attributes('-topmost', True)
        comment_window.transient(self.root)
        comment_window.grab_set()
        
        frame = tk.Frame(comment_window, bg='#ffffff', padx=16, pady=16)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="Comment:", font=('Segoe UI', 10, 'bold'), bg='#ffffff', fg='#1a1a1a').pack(anchor='w')
        comment_entry = tk.Entry(frame, font=('Arial', 11))
        comment_entry.pack(fill=tk.X, pady=(5, 15))
        comment_entry.focus()
        
        def save_comment():
            comment = comment_entry.get().strip()
            for index in selections:
                self.mouse_positions[index]['comment'] = comment
                pos_data = self.mouse_positions[index]
                comment_str = f" - {comment}" if comment else ""
                self.positions_listbox.delete(index)
                self.positions_listbox.insert(index, 
                    f"{index+1}. Position ({pos_data['x']}, {pos_data['y']}) - {len(pos_data['actions'])} actions{comment_str}")
            comment_window.destroy()
        
        tk.Button(frame, text="Save", command=save_comment,
                 bg='#10b981', fg='white', font=('Segoe UI', 9, 'bold'),
                 relief=tk.FLAT, padx=16, pady=8, cursor='hand2').pack()
        
        comment_entry.bind('<Return>', lambda e: save_comment())
    
    def save_macro(self):
        """Save current macro to file"""
        if len(self.mouse_positions) == 0:
            messagebox.showinfo("Save Macro", "No positions to save!")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Macro Files", "*.json"), ("All Files", "*.*")],
            title="Save Macro"
        )
        
        if not filepath:
            return
        
        try:
            macro_data = {
                'mouse_positions': self.mouse_positions,
                'start_actions': self.start_actions,
                'end_actions': self.end_actions
            }
            
            with open(filepath, 'w') as f:
                json.dump(macro_data, f, indent=2)
            
            self.status_label.config(text="Macro saved", fg='#10b981')
            self.root.after(2000, lambda: self.update_ui())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")
    
    def load_macro(self):
        """Load macro from file"""
        filepath = filedialog.askopenfilename(
            filetypes=[("Macro Files", "*.json"), ("All Files", "*.*")],
            title="Load Macro"
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'r') as f:
                macro_data = json.load(f)
            
            self.mouse_positions = macro_data.get('mouse_positions', [])
            self.start_actions = macro_data.get('start_actions', [])
            self.end_actions = macro_data.get('end_actions', [])
            
            # Refresh UI
            self.positions_listbox.delete(0, tk.END)
            for i, pos_data in enumerate(self.mouse_positions, 1):
                comment_str = f" - {pos_data.get('comment', '')}" if pos_data.get('comment') else ""
                self.positions_listbox.insert(tk.END, 
                    f"{i}. Position ({pos_data['x']}, {pos_data['y']}) - {len(pos_data['actions'])} actions{comment_str}")
            
            self.update_actions_summary()
            self.update_ui()
            self.status_label.config(text="Macro loaded", fg='#10b981')
            self.root.after(2000, lambda: self.update_ui())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {e}")
    
    def edit_coordinates(self):
        """Edit coordinates of selected position"""
        selections = self.positions_listbox.curselection()
        if not selections:
            messagebox.showinfo("Edit Coordinates", "Select a position first")
            return
        
        if len(selections) > 1:
            messagebox.showinfo("Edit Coordinates", "Please select only one position to edit coordinates")
            return
        
        index = selections[0]
        pos_data = self.mouse_positions[index]
        
        # Create edit window
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Coordinates")
        edit_window.geometry("350x200")
        edit_window.configure(bg='#ffffff')
        edit_window.attributes('-topmost', True)
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        frame = tk.Frame(edit_window, bg='#f0f0f0', padx=16, pady=16)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="Edit Position Coordinates", font=('Arial', 12, 'bold'), 
                bg='#ffffff', fg='#1a1a1a').pack(pady=(0, 15))
        
        # X coordinate
        x_frame = tk.Frame(frame, bg='#f0f0f0')
        x_frame.pack(fill=tk.X, pady=5)
        tk.Label(x_frame, text="X:", font=('Arial', 10), bg='#f0f0f0', width=3).pack(side=tk.LEFT)
        x_entry = tk.Entry(x_frame, font=('Arial', 11))
        x_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        x_entry.insert(0, str(pos_data['x']))
        
        # Y coordinate
        y_frame = tk.Frame(frame, bg='#f0f0f0')
        y_frame.pack(fill=tk.X, pady=5)
        tk.Label(y_frame, text="Y:", font=('Arial', 10), bg='#f0f0f0', width=3).pack(side=tk.LEFT)
        y_entry = tk.Entry(y_frame, font=('Arial', 11))
        y_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        y_entry.insert(0, str(pos_data['y']))
        
        def save_coordinates():
            try:
                new_x = int(x_entry.get().strip())
                new_y = int(y_entry.get().strip())
                
                pos_data['x'] = new_x
                pos_data['y'] = new_y
                
                # Update display
                comment_str = f" - {pos_data.get('comment', '')}" if pos_data.get('comment') else ""
                self.positions_listbox.delete(index)
                self.positions_listbox.insert(index, 
                    f"{index+1}. Position ({new_x}, {new_y}) - {len(pos_data['actions'])} actions{comment_str}")
                
                edit_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid integer coordinates")
        
        btn_frame = tk.Frame(frame, bg='#f0f0f0')
        btn_frame.pack(pady=(15, 0))
        
        tk.Button(btn_frame, text="Cancel", command=edit_window.destroy,
                 bg='#6b7280', fg='white', font=('Segoe UI', 9),
                 relief=tk.FLAT, padx=16, pady=8, cursor='hand2').pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(btn_frame, text="Save", command=save_coordinates,
                 bg='#10b981', fg='white', font=('Segoe UI', 9, 'bold'),
                 relief=tk.FLAT, padx=16, pady=8, cursor='hand2').pack(side=tk.LEFT)
        
        x_entry.focus()
    
    def delete_positions(self):
        """Delete selected position(s)"""
        selections = self.positions_listbox.curselection()
        if not selections:
            messagebox.showinfo("Delete", "Select position(s) to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Delete {len(selections)} position(s)?"):
            # Delete in reverse order to maintain indices
            for index in reversed(selections):
                del self.mouse_positions[index]
            
            # Refresh list
            self.positions_listbox.delete(0, tk.END)
            for i, pos_data in enumerate(self.mouse_positions, 1):
                comment_str = f" - {pos_data.get('comment', '')}" if pos_data.get('comment') else ""
                self.positions_listbox.insert(tk.END, 
                    f"{i}. Position ({pos_data['x']}, {pos_data['y']}) - {len(pos_data['actions'])} actions{comment_str}")
            
            self.update_ui()
    
    def add_new_position(self):
        """Add a new position manually"""
        # Create add window
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New Position")
        add_window.geometry("350x250")
        add_window.configure(bg='#ffffff')
        add_window.attributes('-topmost', True)
        add_window.transient(self.root)
        add_window.grab_set()
        
        frame = tk.Frame(add_window, bg='#ffffff', padx=16, pady=16)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="Add New Position", font=('Arial', 12, 'bold'), 
                bg='#ffffff', fg='#1a1a1a').pack(pady=(0, 15))
        
        # X coordinate
        x_frame = tk.Frame(frame, bg='#f0f0f0')
        x_frame.pack(fill=tk.X, pady=5)
        tk.Label(x_frame, text="X:", font=('Arial', 10), bg='#f0f0f0', width=3).pack(side=tk.LEFT)
        x_entry = tk.Entry(x_frame, font=('Arial', 11))
        x_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Y coordinate
        y_frame = tk.Frame(frame, bg='#f0f0f0')
        y_frame.pack(fill=tk.X, pady=5)
        tk.Label(y_frame, text="Y:", font=('Arial', 10), bg='#f0f0f0', width=3).pack(side=tk.LEFT)
        y_entry = tk.Entry(y_frame, font=('Arial', 11))
        y_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Use current mouse position button
        def use_current_position():
            x, y = self.mouse_controller.position
            x_entry.delete(0, tk.END)
            x_entry.insert(0, str(x))
            y_entry.delete(0, tk.END)
            y_entry.insert(0, str(y))
        
        tk.Button(frame, text="Use Current Mouse Position", command=use_current_position,
                 bg='#3b82f6', fg='white', font=('Segoe UI', 9),
                 relief=tk.FLAT, padx=12, pady=7, cursor='hand2').pack(pady=10)
        
        def add_position():
            try:
                new_x = int(x_entry.get().strip())
                new_y = int(y_entry.get().strip())
                
                self.mouse_positions.append({'x': new_x, 'y': new_y, 'actions': [], 'comment': ''})
                
                # Update display
                index = len(self.mouse_positions)
                self.positions_listbox.insert(tk.END, f"{index}. Position ({new_x}, {new_y}) - 0 actions")
                self.positions_listbox.see(tk.END)
                
                self.update_ui()
                add_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid integer coordinates")
        
        btn_frame = tk.Frame(frame, bg='#f0f0f0')
        btn_frame.pack(pady=(15, 0))
        
        tk.Button(btn_frame, text="Cancel", command=add_window.destroy,
                 bg='#6b7280', fg='white', font=('Segoe UI', 9),
                 relief=tk.FLAT, padx=16, pady=8, cursor='hand2').pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(btn_frame, text="Add", command=add_position,
                 bg='#10b981', fg='white', font=('Segoe UI', 9, 'bold'),
                 relief=tk.FLAT, padx=16, pady=8, cursor='hand2').pack(side=tk.LEFT)
        
        x_entry.focus()
    
    def run_macro(self):
        """Execute the recorded macro"""
        if len(self.mouse_positions) == 0:
            messagebox.showinfo("Run Macro", "No mouse positions recorded!")
            return
        
        thread = threading.Thread(target=self._execute_macro, daemon=True)
        thread.start()
        
    def _execute_macro(self):
        """Execute macro actions"""
        self.root.after(0, lambda: self.status_label.config(text="Running macro...", fg='#3b82f6'))
        
        time.sleep(0.5)
        
        # Execute start actions
        for action in self.start_actions:
            self.execute_action(action)
        
        # For each mouse position
        for pos_data in self.mouse_positions:
            # Move to position
            self.mouse_controller.position = (pos_data['x'], pos_data['y'])
            time.sleep(0.05)
            
            # Execute this position's actions
            for action in pos_data['actions']:
                self.execute_action(action)
        
        # Execute end actions
        for action in self.end_actions:
            self.execute_action(action)
        
        self.root.after(0, lambda: self.status_label.config(text="Macro completed", fg='#10b981'))
        self.root.after(2000, lambda: self.update_ui())
    
    def execute_action(self, action):
        """Execute a single action"""
        action_type = action['type']
        
        if action_type == 'click':
            button = Button.left if action['button'] == 'left' else Button.right
            self.mouse_controller.click(button)
            time.sleep(0.05)
            
        elif action_type == 'key_press':
            key = action['key']
            duration = action.get('duration', 0)
            
            self.keyboard_controller.press(key)
            if duration > 0:
                time.sleep(duration)
            else:
                time.sleep(0.01)
            self.keyboard_controller.release(key)
            
        elif action_type == 'key_down':
            key = action['key']
            self.keyboard_controller.press(key)
            
        elif action_type == 'key_up':
            key = action['key']
            self.keyboard_controller.release(key)
            
        elif action_type == 'wait':
            time.sleep(action['duration'])
    
    def run(self):
        """Start the application"""
        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()
        
        self.root.mainloop()
        listener.stop()


class ActionEditor:
    def __init__(self, parent, start_actions, end_actions, save_callback):
        self.start_actions = start_actions.copy()
        self.end_actions = end_actions.copy()
        self.save_callback = save_callback
        
        self.current_list = 'start'  # 'start' or 'end'
        
        self.window = tk.Toplevel(parent)
        self.window.title("Action Editor")
        self.window.geometry("800x650")
        self.window.configure(bg='#ffffff')
        self.window.attributes('-topmost', True)
        
        self.setup_editor_ui()
        self.refresh_list()
        
    def setup_editor_ui(self):
        """Setup editor UI"""
        main_frame = tk.Frame(self.window, bg='#ffffff', padx=16, pady=16)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(main_frame, text="Action Editor", 
                font=('Segoe UI', 14, 'bold'), bg='#ffffff', fg='#1a1a1a').pack(pady=(0, 10))
        
        # Category selector
        cat_frame = tk.Frame(main_frame, bg='#ffffff')
        cat_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(cat_frame, text="Edit Actions For:", 
                font=('Segoe UI', 10, 'bold'), bg='#ffffff', fg='#1a1a1a').pack(side=tk.LEFT, padx=(0, 15))
        
        self.category_var = tk.StringVar(value='start')
        
        tk.Radiobutton(cat_frame, text="Start of Script", variable=self.category_var, 
                      value='start', command=self.change_category, bg='#ffffff',
                      font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=5)
        
        tk.Radiobutton(cat_frame, text="End of Script", variable=self.category_var,
                      value='end', command=self.change_category, bg='#ffffff',
                      font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=5)
        
        # Actions list
        list_frame = tk.Frame(main_frame, bg='white', relief=tk.FLAT, bd=1)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.editor_listbox = tk.Listbox(list_frame, font=('Courier', 9), 
                                        bg='white', fg='#333',
                                        yscrollcommand=scrollbar.set,
                                        relief=tk.FLAT, bd=0, highlightthickness=0)
        self.editor_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.config(command=self.editor_listbox.yview)
        
        # Buttons
        btn_frame = tk.Frame(main_frame, bg='#ffffff')
        btn_frame.pack(fill=tk.X)
        
        tk.Button(btn_frame, text="Add Action", command=self.add_action,
                 bg='#3b82f6', fg='white', font=('Segoe UI', 9),
                 relief=tk.FLAT, padx=12, pady=7, cursor='hand2').pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Button(btn_frame, text="Edit", command=self.edit_selected,
                 bg='#6b7280', fg='white', font=('Segoe UI', 9),
                 relief=tk.FLAT, padx=12, pady=7, cursor='hand2').pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Button(btn_frame, text="Delete", command=self.delete_selected,
                 bg='#ef4444', fg='white', font=('Segoe UI', 9),
                 relief=tk.FLAT, padx=12, pady=7, cursor='hand2').pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Button(btn_frame, text="Move Up", command=self.move_up,
                 bg='#6b7280', fg='white', font=('Segoe UI', 9),
                 relief=tk.FLAT, padx=12, pady=7, cursor='hand2').pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Button(btn_frame, text="Move Down", command=self.move_down,
                 bg='#6b7280', fg='white', font=('Segoe UI', 9),
                 relief=tk.FLAT, padx=12, pady=7, cursor='hand2').pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Button(btn_frame, text="Save & Close", command=self.save_and_close,
                 bg='#10b981', fg='white', font=('Segoe UI', 9, 'bold'),
                 relief=tk.FLAT, padx=16, pady=8, cursor='hand2').pack(side=tk.RIGHT)
    
    def change_category(self):
        """Change the current action category"""
        self.current_list = self.category_var.get()
        self.refresh_list()
    
    def get_current_list(self):
        """Get the currently selected action list"""
        if self.current_list == 'start':
            return self.start_actions
        else:
            return self.end_actions
    
    def refresh_list(self):
        """Refresh the editor listbox"""
        self.editor_listbox.delete(0, tk.END)
        actions = self.get_current_list()
        
        for i, action in enumerate(actions, 1):
            display = self.format_action(action, i)
            self.editor_listbox.insert(tk.END, display)
    
    def format_action(self, action, index):
        """Format action for display"""
        action_type = action['type']
        
        if action_type == 'click':
            return f"{index}. Click {action['button']} button"
            
        elif action_type == 'key_press':
            duration = action.get('duration', 0)
            if duration > 0:
                return f"{index}. Press '{action['key']}' for {duration}s"
            else:
                return f"{index}. Press '{action['key']}'"
                
        elif action_type == 'key_down':
            return f"{index}. Hold down '{action['key']}'"
            
        elif action_type == 'key_up':
            return f"{index}. Release '{action['key']}'"
            
        elif action_type == 'wait':
            return f"{index}. Wait {action['duration']}s"
            
        return f"{index}. {action_type}"
    
    def add_action(self):
        """Add new action"""
        AddActionDialog(self.window, self.get_current_list(), self.refresh_list)
    
    def edit_selected(self):
        """Edit selected action"""
        selection = self.editor_listbox.curselection()
        if not selection:
            messagebox.showinfo("Edit", "Please select an action to edit")
            return
        
        index = selection[0]
        action = self.get_current_list()[index]
        ActionDialog(self.window, action['type'], self.get_current_list(), 
                    self.refresh_list, existing_action=action, index=index)
    
    def delete_selected(self):
        """Delete selected action"""
        selection = self.editor_listbox.curselection()
        if not selection:
            messagebox.showinfo("Delete", "Please select an action to delete")
            return
        
        index = selection[0]
        del self.get_current_list()[index]
        self.refresh_list()
    
    def move_up(self):
        """Move selected action up"""
        selection = self.editor_listbox.curselection()
        if not selection or selection[0] == 0:
            return
        
        index = selection[0]
        actions = self.get_current_list()
        actions[index], actions[index-1] = actions[index-1], actions[index]
        self.refresh_list()
        self.editor_listbox.selection_set(index-1)
    
    def move_down(self):
        """Move selected action down"""
        actions = self.get_current_list()
        selection = self.editor_listbox.curselection()
        if not selection or selection[0] == len(actions) - 1:
            return
        
        index = selection[0]
        actions[index], actions[index+1] = actions[index+1], actions[index]
        self.refresh_list()
        self.editor_listbox.selection_set(index+1)
    
    def save_and_close(self):
        """Save and close"""
        self.save_callback(self.start_actions, self.end_actions)
        self.window.destroy()


class AddActionDialog:
    def __init__(self, parent, actions_list, refresh_callback):
        self.actions_list = actions_list
        self.refresh_callback = refresh_callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Action")
        self.dialog.geometry("400x350")
        self.dialog.configure(bg='#ffffff')
        self.dialog.attributes('-topmost', True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup add action dialog"""
        frame = tk.Frame(self.dialog, bg='#ffffff', padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="Select Action Type", font=('Segoe UI', 12, 'bold'),
                bg='#ffffff', fg='#1a1a1a').pack(pady=(0, 20))
        
        actions = [
            ("Click Mouse", "click"),
            ("Press Key", "key_press"),
            ("Hold Down Key", "key_down"),
            ("Release Key", "key_up"),
            ("Wait/Delay", "wait")
        ]
        
        for text, action_type in actions:
            btn = tk.Button(frame, text=text, 
                     command=lambda at=action_type: self.open_params(at),
                     bg='#3b82f6', fg='white', font=('Segoe UI', 9),
                     relief=tk.FLAT, width=20, pady=10, cursor='hand2')
            btn.pack(pady=5)
    
    def open_params(self, action_type):
        """Open parameters dialog"""
        self.dialog.destroy()
        ActionDialog(self.dialog.master, action_type, self.actions_list, self.refresh_callback)


class ActionDialog:
    def __init__(self, parent, action_type, actions_list, refresh_callback, 
                 existing_action=None, index=None):
        self.action_type = action_type
        self.actions_list = actions_list
        self.refresh_callback = refresh_callback
        self.existing_action = existing_action
        self.index = index
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"{'Edit' if existing_action else 'Add'} Action")
        self.dialog.geometry("450x300")
        self.dialog.configure(bg='#f0f0f0')
        self.dialog.attributes('-topmost', True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup parameters UI"""
        frame = tk.Frame(self.dialog, bg='#ffffff', padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        title_map = {
            'click': 'Click Mouse',
            'key_press': 'Press Key',
            'key_down': 'Hold Down Key',
            'key_up': 'Release Key',
            'wait': 'Wait/Delay'
        }
        
        tk.Label(frame, text=title_map.get(self.action_type, self.action_type), 
                font=('Segoe UI', 12, 'bold'), bg='#ffffff', fg='#1a1a1a').pack(pady=(0, 20))
        
        self.entries = {}
        
        if self.action_type == 'click':
            tk.Label(frame, text="Button:", bg='#ffffff', fg='#1a1a1a', font=('Segoe UI', 10)).pack(anchor='w')
            self.entries['button'] = ttk.Combobox(frame, values=['left', 'right', 'middle'],
                                                 font=('Arial', 10), state='readonly')
            self.entries['button'].pack(fill=tk.X, pady=(0, 15))
            if self.existing_action:
                self.entries['button'].set(self.existing_action.get('button', 'left'))
            else:
                self.entries['button'].set('left')
        
        elif self.action_type in ['key_press', 'key_down', 'key_up']:
            tk.Label(frame, text="Key (e.g., 'a', '3', 'space', 'shift'):", 
                    bg='#ffffff', fg='#1a1a1a', font=('Segoe UI', 10)).pack(anchor='w')
            self.entries['key'] = tk.Entry(frame, font=('Arial', 11))
            self.entries['key'].pack(fill=tk.X, pady=(0, 15))
            if self.existing_action:
                self.entries['key'].insert(0, str(self.existing_action.get('key', '')))
            
            if self.action_type == 'key_press':
                tk.Label(frame, text="Hold Duration (seconds, 0 for tap):", 
                        bg='#ffffff', fg='#1a1a1a', font=('Segoe UI', 10)).pack(anchor='w')
                self.entries['duration'] = tk.Entry(frame, font=('Arial', 11))
                self.entries['duration'].pack(fill=tk.X, pady=(0, 15))
                if self.existing_action:
                    self.entries['duration'].insert(0, str(self.existing_action.get('duration', 0)))
                else:
                    self.entries['duration'].insert(0, '0')
        
        elif self.action_type == 'wait':
            tk.Label(frame, text="Duration (seconds):", 
                    bg='#ffffff', fg='#1a1a1a', font=('Segoe UI', 10)).pack(anchor='w')
            self.entries['duration'] = tk.Entry(frame, font=('Arial', 11))
            self.entries['duration'].pack(fill=tk.X, pady=(0, 15))
            if self.existing_action:
                self.entries['duration'].insert(0, str(self.existing_action.get('duration', '')))
        
        # Buttons
        btn_frame = tk.Frame(frame, bg='#ffffff')
        btn_frame.pack(pady=(20, 0))
        
        tk.Button(btn_frame, text="Cancel", command=self.dialog.destroy,
                 bg='#6b7280', fg='white', font=('Segoe UI', 9),
                 relief=tk.FLAT, padx=16, pady=8, cursor='hand2').pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(btn_frame, text="Save", command=self.save_action,
                 bg='#10b981', fg='white', font=('Segoe UI', 9, 'bold'),
                 relief=tk.FLAT, padx=16, pady=8, cursor='hand2').pack(side=tk.LEFT)
    
    def save_action(self):
        """Save the action"""
        try:
            action = {'type': self.action_type}
            
            if self.action_type == 'click':
                action['button'] = self.entries['button'].get()
            
            elif self.action_type in ['key_press', 'key_down', 'key_up']:
                key = self.entries['key'].get().strip()
                if not key:
                    messagebox.showerror("Error", "Please enter a key")
                    return
                action['key'] = key
                
                if self.action_type == 'key_press':
                    action['duration'] = float(self.entries['duration'].get())
            
            elif self.action_type == 'wait':
                action['duration'] = float(self.entries['duration'].get())
            
            if self.existing_action and self.index is not None:
                self.actions_list[self.index] = action
            else:
                self.actions_list.append(action)
            
            self.refresh_callback()
            self.dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")


class PositionActionEditor:
    def __init__(self, parent, actions, save_callback, pos_num):
        self.actions = actions.copy()
        self.save_callback = save_callback
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"Actions for Position {pos_num}")
        self.window.geometry("800x650")
        self.window.configure(bg='#ffffff')
        self.window.attributes('-topmost', True)
        
        self.setup_editor_ui()
        self.refresh_list()
        
    def setup_editor_ui(self):
        """Setup editor UI"""
        main_frame = tk.Frame(self.window, bg='#ffffff', padx=16, pady=16)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(main_frame, text="Position Action Editor", 
                font=('Segoe UI', 14, 'bold'), bg='#ffffff', fg='#1a1a1a').pack(pady=(0, 10))
        
        # Actions list
        list_frame = tk.Frame(main_frame, bg='white', relief=tk.FLAT, bd=1)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.editor_listbox = tk.Listbox(list_frame, font=('Courier', 9), 
                                        bg='white', fg='#333',
                                        yscrollcommand=scrollbar.set,
                                        relief=tk.FLAT, bd=0, highlightthickness=0)
        self.editor_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.config(command=self.editor_listbox.yview)
        
        # Buttons
        btn_frame = tk.Frame(main_frame, bg='#ffffff')
        btn_frame.pack(fill=tk.X)
        
        tk.Button(btn_frame, text="Add Action", command=self.add_action,
                 bg='#3b82f6', fg='white', font=('Segoe UI', 9),
                 relief=tk.FLAT, padx=12, pady=7, cursor='hand2').pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Button(btn_frame, text="Edit", command=self.edit_selected,
                 bg='#6b7280', fg='white', font=('Segoe UI', 9),
                 relief=tk.FLAT, padx=12, pady=7, cursor='hand2').pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Button(btn_frame, text="Delete", command=self.delete_selected,
                 bg='#ef4444', fg='white', font=('Segoe UI', 9),
                 relief=tk.FLAT, padx=12, pady=7, cursor='hand2').pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Button(btn_frame, text="Move Up", command=self.move_up,
                 bg='#6b7280', fg='white', font=('Segoe UI', 9),
                 relief=tk.FLAT, padx=12, pady=7, cursor='hand2').pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Button(btn_frame, text="Move Down", command=self.move_down,
                 bg='#6b7280', fg='white', font=('Segoe UI', 9),
                 relief=tk.FLAT, padx=12, pady=7, cursor='hand2').pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Button(btn_frame, text="Save & Close", command=self.save_and_close,
                 bg='#10b981', fg='white', font=('Segoe UI', 9, 'bold'),
                 relief=tk.FLAT, padx=16, pady=8, cursor='hand2').pack(side=tk.RIGHT)
    
    def refresh_list(self):
        """Refresh the editor listbox"""
        self.editor_listbox.delete(0, tk.END)
        
        for i, action in enumerate(self.actions, 1):
            display = self.format_action(action, i)
            self.editor_listbox.insert(tk.END, display)
    
    def format_action(self, action, index):
        """Format action for display"""
        action_type = action['type']
        
        if action_type == 'click':
            return f"{index}. Click {action['button']} button"
            
        elif action_type == 'key_press':
            duration = action.get('duration', 0)
            if duration > 0:
                return f"{index}. Press '{action['key']}' for {duration}s"
            else:
                return f"{index}. Press '{action['key']}'"
                
        elif action_type == 'key_down':
            return f"{index}. Hold down '{action['key']}'"
            
        elif action_type == 'key_up':
            return f"{index}. Release '{action['key']}'"
            
        elif action_type == 'wait':
            return f"{index}. Wait {action['duration']}s"
            
        return f"{index}. {action_type}"
    
    def add_action(self):
        """Add new action"""
        AddActionDialog(self.window, self.actions, self.refresh_list)
    
    def edit_selected(self):
        """Edit selected action"""
        selection = self.editor_listbox.curselection()
        if not selection:
            messagebox.showinfo("Edit", "Please select an action to edit")
            return
        
        index = selection[0]
        action = self.actions[index]
        ActionDialog(self.window, action['type'], self.actions, 
                    self.refresh_list, existing_action=action, index=index)
    
    def delete_selected(self):
        """Delete selected action"""
        selection = self.editor_listbox.curselection()
        if not selection:
            messagebox.showinfo("Delete", "Please select an action to delete")
            return
        
        index = selection[0]
        del self.actions[index]
        self.refresh_list()
    
    def move_up(self):
        """Move selected action up"""
        selection = self.editor_listbox.curselection()
        if not selection or selection[0] == 0:
            return
        
        index = selection[0]
        self.actions[index], self.actions[index-1] = self.actions[index-1], self.actions[index]
        self.refresh_list()
        self.editor_listbox.selection_set(index-1)
    
    def move_down(self):
        """Move selected action down"""
        selection = self.editor_listbox.curselection()
        if not selection or selection[0] == len(self.actions) - 1:
            return
        
        index = selection[0]
        self.actions[index], self.actions[index+1] = self.actions[index+1], self.actions[index]
        self.refresh_list()
        self.editor_listbox.selection_set(index+1)
    
    def save_and_close(self):
        """Save and close"""
        self.save_callback(self.actions)
        self.window.destroy()
if __name__ == "__main__":
    recorder = MacroRecorder()
    recorder.run()
