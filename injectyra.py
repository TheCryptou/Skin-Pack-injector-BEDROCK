import os
import shutil
import ctypes
import sys
import glob
from tkinter import filedialog, Tk, messagebox, Toplevel, Label, Listbox, Scrollbar, VERTICAL, RIGHT, Y, END, StringVar, Radiobutton, Button
import threading

def is_admin():
    """Check if the script is running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def request_admin_privileges():
    """Request administrator privileges if not already running as admin"""
    if not is_admin():
        # Re-run the script with admin privileges
        ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas", 
            sys.executable, 
            " ".join(sys.argv), 
            None, 
            1
        )
        return False
    return True

def find_minecraft_directory():
    """Find the Minecraft Bedrock directory dynamically"""
    # Look for Minecraft directories in WindowsApps
    minecraft_base_path = r"C:\Program Files\WindowsApps"
    
    if not os.path.exists(minecraft_base_path):
        return None
    
    # Look for directories that match the Minecraft pattern
    minecraft_dirs = glob.glob(os.path.join(minecraft_base_path, "MICROSOFT.MINECRAFTUWP_*"))
    
    # Filter for directories that have the data\skin_packs subdirectory
    for dir_path in minecraft_dirs:
        skin_packs_path = os.path.join(dir_path, "data", "skin_packs")
        if os.path.exists(skin_packs_path):
            return skin_packs_path
    
    return None

def select_location():
    """Allow user to select between persona and custom locations"""
    root = Tk()
    root.title("Select Skin Pack Location")
    root.geometry("300x150")
    root.resizable(False, False)
    
    # Variable to store the selection
    location_var = StringVar(value="custom")
    
    # Add labels and radio buttons
    Label(root, text="Select Skin Pack Location:", font=("Arial", 12, "bold")).pack(pady=10)
    
    Radiobutton(root, text="Emplacement 1 (Persona)", variable=location_var, value="persona").pack(anchor="w", padx=20)
    Radiobutton(root, text="Emplacement 2 (Custom)", variable=location_var, value="custom").pack(anchor="w", padx=20)
    
    # OK button
    def on_ok():
        root.destroy()
    
    ok_button = Button(root, text="OK", command=on_ok)
    ok_button.pack(pady=20)
    
    # Center the window
    root.eval('tk::PlaceWindow . center')
    
    # Wait for user to close the window
    root.mainloop()
    
    return location_var.get()

def show_progress_window(messages):
    """Show a simple window with progress messages"""
    progress_window = Toplevel()
    progress_window.title("Skin Pack Injection Progress")
    progress_window.geometry("600x400")
    progress_window.resizable(True, True)
    
    # Create listbox with scrollbar
    listbox = Listbox(progress_window, width=80, height=20)
    scrollbar = Scrollbar(progress_window, orient=VERTICAL, command=listbox.yview)
    listbox.configure(yscrollcommand=scrollbar.set)
    
    listbox.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scrollbar.pack(side=RIGHT, fill=Y, pady=10)
    
    # Add messages to listbox
    for message in messages:
        listbox.insert(END, message)
    
    # Select last item
    listbox.see(END)
    
    # Add close button
    close_button = Label(progress_window, text="Close", fg="blue", cursor="hand2")
    close_button.pack(pady=5)
    close_button.bind("<Button-1>", lambda e: progress_window.destroy())
    
    return progress_window

def select_folder():
    """Open a dialog for the user to select a folder"""
    root = Tk()
    root.withdraw()  # Hide the main window
    folder_selected = filedialog.askdirectory(title="Select Skin Pack Folder")
    root.destroy()
    return folder_selected

def inject_skin_pack(source_folder, target_location, messages):
    """Inject the skin pack into Minecraft Bedrock"""
    try:
        # Find the Minecraft skin packs directory dynamically
        messages.append("Searching for Minecraft installation...")
        minecraft_skin_packs_dir = find_minecraft_directory()
        
        if not minecraft_skin_packs_dir:
            messages.append("ERROR: Minecraft skin packs directory not found.")
            messages.append("Make sure Minecraft Bedrock Edition is installed.")
            return False
        
        messages.append(f"Found Minecraft directory: {minecraft_skin_packs_dir}")
        
        # Determine target folder based on user selection
        target_folder = os.path.join(minecraft_skin_packs_dir, target_location)
        messages.append(f"Selected location: {target_location}")
        
        # Delete the target folder if it exists
        if os.path.exists(target_folder):
            messages.append(f"Deleting existing {target_location} folder...")
            try:
                shutil.rmtree(target_folder)
                messages.append(f"Deleted existing {target_location} folder.")
            except Exception as e:
                messages.append(f"ERROR deleting {target_location} folder: {e}")
                return False
        else:
            messages.append(f"No existing {target_location} folder found.")
        
        # Create a new target folder
        messages.append(f"Creating new {target_location} folder...")
        try:
            os.makedirs(target_folder)
            messages.append(f"Created new {target_location} folder.")
        except Exception as e:
            messages.append(f"ERROR creating {target_location} folder: {e}")
            return False
        
        # Copy all files from the source folder to the target folder
        messages.append(f"Copying files to {target_location} folder...")
        try:
            for item in os.listdir(source_folder):
                source_item = os.path.join(source_folder, item)
                destination_item = os.path.join(target_folder, item)
                
                # Copy files and folders
                if os.path.isfile(source_item):
                    shutil.copy2(source_item, destination_item)
                    messages.append(f"Copied file: {item}")
                elif os.path.isdir(source_item):
                    shutil.copytree(source_item, destination_item)
                    messages.append(f"Copied folder: {item}")
            
            messages.append("All files copied successfully!")
            messages.append("Skin pack injection completed successfully!")
            return True
            
        except Exception as e:
            messages.append(f"ERROR copying files: {e}")
            return False
            
    except Exception as e:
        messages.append(f"Unexpected error: {e}")
        return False

def main():
    # Check for admin privileges
    if not request_admin_privileges():
        return
    
    # Ask user to select location (persona or custom)
    target_location = select_location()
    
    # Ask user to select a folder
    source_folder = select_folder()
    
    if not source_folder:
        messagebox.showerror("Error", "No folder selected. Exiting.")
        return
    
    if not os.path.exists(source_folder):
        messagebox.showerror("Error", "Selected folder does not exist. Exiting.")
        return
    
    # Messages list to store progress
    messages = [f"Selected folder: {source_folder}", f"Selected location: {target_location}"]
    
    # Perform injection
    success = inject_skin_pack(source_folder, target_location, messages)
    
    # Show results
    root = Tk()
    root.withdraw()  # Hide the main window
    
    if success:
        messages.append("\nSUCCESS: Skin pack injected successfully!")
        messages.append("You can now launch Minecraft Bedrock Edition.")
        show_progress_window(messages)
        messagebox.showinfo("Success", "Skin pack injected successfully!\nYou can now launch Minecraft.")
    else:
        messages.append("\nERROR: Failed to inject skin pack.")
        show_progress_window(messages)
        messagebox.showerror("Error", "Failed to inject skin pack. Check the log for details.")
    
    root.destroy()

if __name__ == "__main__":
    main()
