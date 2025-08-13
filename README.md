# ⚽ FPL Mini-League Analyzer

A comprehensive **Fantasy Premier League (FPL) Mini-League Analysis Tool** built with Streamlit that provides real-time gameweek tracking, historical performance analysis, and pre-season insights for your FPL mini-league.

## 🌟 Features

### 🎮 Live Gameweek Dashboard
- **Real-time Points Tracking**: Monitor live points for all managers during active gameweeks
- **Current Leader Display**: Prominently shows the gameweek leader with their points
- **Detailed Player Breakdown**: See each manager's players, points, captain choices, and bench performance
- **Transfer Tracking**: Monitor transfers made and associated costs
- **Position-wise Analysis**: Points breakdown by position (GK, DEF, MID, FWD)

### 📊 Overall Statistics
- **Season Leaderboard**: Complete standings with total points and rankings
- **Points Heatmap**: Visual representation of points distribution across gameweeks
- **Weekly Winners**: Track who won each individual gameweek
- **Performance Metrics**: 
  - Average points per gameweek
  - Consistency analysis (standard deviation)
  - Best and worst gameweek performances
- **Manager Comparison**: Interactive tool to compare selected managers' performance over time

### ⏰ Pre-Season Support
- **Season Detection**: Automatically detects when the FPL season hasn't started
- **Manager Welcome**: Beautiful card display of all league members
- **Clickable Team Links**: Direct links to each manager's FPL team page
- **Last Season Statistics**: Comprehensive table showing previous season performance including:
  - Total points from last season
  - Overall FPL rank
  - Season comparison metrics

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- FPL Mini-League ID

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/fpl-mini-league-analyzer.git
cd fpl-mini-league-analyzer
```

2. **Install required packages**
```bash
pip install streamlit requests pandas plotly numpy
```

3. **Update your league ID**
   - Open the Python file
   - Replace `469324` with your FPL mini-league ID in the following lines:
   ```python
   league_data = fetch_data("https://fantasy.premierleague.com/api/leagues-classic/YOUR_LEAGUE_ID/standings/")
   ```

4. **Run the application**
```bash
streamlit run fpl_live.py
```

## 🔧 Configuration

### Finding Your League ID
1. Go to your FPL mini-league page
2. Look at the URL: `https://fantasy.premierleague.com/leagues/YOUR_LEAGUE_ID/standings/`
3. Copy the number after `/leagues/` and before `/standings/`

### Customization Options
- **Auto-refresh**: Toggle automatic refresh every 2 minutes
- **League Name**: Automatically pulled from FPL API
- **Visual Themes**: Gradient cards and color schemes can be customized in the CSS sections

## 📱 Usage

### During FPL Season
1. **Live Gameweek Tab**: 
   - View real-time points and standings
   - See detailed player performance
   - Monitor transfers and captain choices

2. **Overall Statistics Tab**:
   - Analyze season-long performance
   - Compare managers head-to-head
   - View historical trends and patterns

### Pre-Season
- Displays welcome message with all league managers
- Shows clickable team cards linking to FPL profiles
- Presents last season performance statistics

## 🎯 Key Features Explained

### Live Points Calculation
- **Player Points**: Base points × captain multiplier
- **Transfer Costs**: -4 points for each transfer above the free limit
- **Chip Usage**: Accounts for Free Hit, Triple Captain, etc.

### Visual Elements
- **Gradient Cards**: Beautiful manager display cards
- **Interactive Heatmaps**: Points distribution visualization
- **Responsive Design**: Works on desktop and mobile devices
- **Hover Effects**: Enhanced user interaction

### Data Sources
- **Official FPL API**: All data sourced directly from Fantasy Premier League
- **Real-time Updates**: Live data during gameweeks
- **Historical Data**: Access to previous seasons and gameweeks

## 🔄 Auto-Refresh Feature

The app includes an optional auto-refresh feature that:
- Refreshes data every 2 minutes when enabled
- Can be toggled on/off via sidebar checkbox
- Useful during live gameweeks for real-time tracking

## 📊 Statistics & Analytics

### Performance Metrics
- **Consistency Score**: Standard deviation of weekly points
- **Average Points**: Season average per gameweek
- **Peak Performance**: Highest single gameweek score
- **Weekly Wins**: Number of gameweeks won by each manager

### Visual Analytics
- **Heatmap**: Color-coded points distribution
- **Line Charts**: Performance trends over time
- **Bar Charts**: Weekly winners and comparative analysis
- **Gradient Tables**: Easy-to-read statistical tables

## 🛠️ Technical Details

### Dependencies
- **Streamlit**: Web app framework
- **Requests**: API data fetching
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **NumPy**: Numerical calculations

### API Endpoints Used
- Bootstrap data: Player and team information
- Live gameweek data: Real-time points and statistics
- League standings: Current season rankings
- Manager history: Previous season performance
- Transfer data: Manager transfer activity

### Error Handling
- Graceful API failure handling
- Fallback data sources during pre-season
- Data validation and cleaning
- User-friendly error messages

## 🎨 Customization

### Styling
The app uses custom CSS for:
- Gradient background cards
- Responsive grid layouts
- Hover animations
- Color schemes and themes

### Layout Options
- 3-column manager card grid
- Responsive table displays
- Interactive chart configurations
- Mobile-optimized designs

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Fantasy Premier League** for providing the official API
- **Streamlit** for the excellent web app framework
- **Plotly** for interactive visualization capabilities

## 📞 Support

If you encounter any issues or have questions:
1. Check if your league ID is correctly configured
2. Ensure all dependencies are installed
3. Verify internet connection for API access
4. Open an issue on GitHub for bug reports

## 🔮 Future Enhancements

- **Player Performance Analysis**: Detailed player statistics
- **Trade Suggestions**: AI-powered transfer recommendations
- **Mobile App**: Native mobile application
- **League Predictions**: Performance forecasting
- **Social Features**: Manager messaging and challenges

---

**Enjoy tracking your FPL mini-league! 🏆⚽**