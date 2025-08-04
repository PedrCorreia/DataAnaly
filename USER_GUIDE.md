# Data Analysis Pro - User Guide

## Data Import Features

### Supported File Types
- **CSV Files** (*.csv) - Comma-separated values
- **Text Files** (*.txt, *.tsv) - Tab-separated or custom delimited
- **Excel Files** (*.xlsx, *.xls) - Microsoft Excel spreadsheets

### Quick Presets
The application includes several quick presets for common data formats:

1. **Default CSV** - Standard comma-separated values with UTF-8 encoding
2. **European CSV (;)** - Semicolon-separated with comma as decimal separator
3. **Tab Separated** - Tab-delimited text files
4. **Pipe Delimited** - Pipe (|) separated values
5. **Excel** - Standard Excel file import
6. **Custom** - User-defined advanced settings

### Advanced Settings
Click the "⚙️ Advanced Settings" button to access detailed import options:

#### CSV/Text File Options:
- **Separator**: Choose or specify custom column delimiter
- **Encoding**: File encoding (UTF-8, Latin1, CP1252, ASCII)
- **Header Row**: Specify which row contains column headers
- **Decimal Separator**: Decimal point character (. or ,)
- **Thousands Separator**: Thousands grouping character
- **Skip Rows**: Number of rows to skip at the beginning
- **Max Rows**: Maximum number of rows to read (0 = all)
- **Date Parsing**: Automatically parse date columns
- **NA Values**: Custom missing value indicators
- **Quote Character**: Text qualifier character
- **Comment Character**: Comment line indicator

#### Excel File Options:
- **Sheet Selection**: Choose specific worksheet
- **Header Row**: Row number containing column headers
- **Skip Rows**: Number of rows to skip
- **Max Rows**: Maximum rows to import
- **Date Parsing**: Auto-parse date columns
- **NA Values**: Custom missing value indicators

### Sample Data Files
The application includes sample data files in the `sample_data/` folder:

- `sales_data.csv` - Standard CSV format
- `european_data.csv` - European format (semicolon separator, comma decimal)
- `tab_separated_data.txt` - Tab-delimited text file
- `pipe_delimited_data.txt` - Pipe-delimited format

### Testing the Import Features

1. **Start the Application**:
   ```
   python main.py
   ```

2. **Test Different Presets**:
   - Load `sample_data/sales_data.csv` with "Default CSV" preset
   - Load `sample_data/european_data.csv` with "European CSV (;)" preset
   - Load `sample_data/tab_separated_data.txt` with "Tab Separated" preset
   - Load `sample_data/pipe_delimited_data.txt` with "Pipe Delimited" preset

3. **Test Advanced Settings**:
   - Click "⚙️ Advanced Settings" to customize import parameters
   - Try different encoding options for international data
   - Experiment with skip rows and max rows settings
   - Test custom separators and decimal formats

4. **Test Auto-Detection**:
   - Use "Auto-detect" preset with different file formats
   - The system will try common separators automatically

### Features Overview

#### Data Preview
- View first 100 rows of imported data
- Resizable columns
- Row selection and highlighting

#### Metadata Display
- Total rows and columns count
- Missing values statistics
- Memory usage information
- File size details
- Column type distribution

#### Column Information
- List of numeric vs categorical columns
- Data type summary
- Column statistics

### Professional UI Features
- **Modern Qt-based interface** with native look and feel
- **Dark/Light theme support** (system-aware)
- **Tabbed interface** for different analysis functions
- **Status bar** with loading progress and messages
- **Comprehensive menu system** with keyboard shortcuts
- **Help system** with User Guide, Shortcuts, and About dialogs
- **Responsive layout** that adapts to window resizing

### Help & Support Features

#### Help Menu (accessible from menu bar):
1. **User Guide (F1)** - Comprehensive quick-start guide with:
   - Getting started steps
   - Data import features overview
   - Plotting capabilities
   - Keyboard shortcuts
   - Pro tips for advanced usage

2. **Keyboard Shortcuts (Ctrl+?)** - Complete list of shortcuts including:
   - File operations (Ctrl+N, Ctrl+O, Ctrl+Q)
   - View controls (Ctrl+T for theme toggle)
   - Tab navigation (Ctrl+1-4)
   - Plotting shortcuts (Ctrl+E for export)
   - Help shortcuts (F1, Ctrl+?)

3. **About Dialog** - Detailed application information:
   - Version and build information
   - Feature overview with descriptions
   - Technical stack details
   - Professional UI advantages over tkinter

#### Menu System:
- **File Menu**: New Project, Open Data, Exit
- **View Menu**: Toggle Theme, Tab navigation
- **Help Menu**: User Guide, Shortcuts, About

This professional interface provides a much better user experience compared to tkinter, with:
- Native OS integration
- High DPI display support
- Professional styling and theming
- Better performance with large datasets
- Advanced widgets and controls
