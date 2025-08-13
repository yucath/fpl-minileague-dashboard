import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

st.set_page_config(layout="wide", page_title="FPL Mini-League Analyzer")

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None

def check_season_started(bootstrap_data):
    """Check if the current season has started"""
    if not bootstrap_data or 'events' not in bootstrap_data:
        return False, 0
    
    # Check if any gameweek has started
    current_gw = None
    for event in bootstrap_data['events']:
        if event['is_current']:
            current_gw = event['id']
            break
    
    # If no current gameweek or current gameweek is 0/1 and hasn't started
    if current_gw is None or current_gw <= 1:
        # Check if GW1 has actually started by looking at deadline_time
        gw1 = next((event for event in bootstrap_data['events'] if event['id'] == 1), None)
        if gw1:
            deadline = datetime.fromisoformat(gw1['deadline_time'].replace('Z', '+00:00'))
            if datetime.now().astimezone() < deadline:
                return False, 0
    
    return True, current_gw or 1

def get_previous_season_data(team_id):
    """Get previous season data for a team"""
    history = fetch_data(f"https://fantasy.premierleague.com/api/entry/{team_id}/history/")
    if not history or 'past' not in history:
        return None
    
    # Get the most recent past season
    past_seasons = history['past']
    if not past_seasons:
        return None
    
    # Sort by season start date and get the most recent
    most_recent = sorted(past_seasons, key=lambda x: x['season_name'], reverse=True)[0]
    
    return {
        'season': most_recent['season_name'],
        'total_points': most_recent['total_points'],
        'rank': most_recent['rank']
    }

def show_preseason_message():
    """Display pre-season message with welcome to managers"""
    st.markdown(
        """
        <div style='background-color: #ff6b35; padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 30px;'>
            <h1 style='color: white; font-size: 64px; margin: 20px 0;'>⏰</h1>
            <h2 style='color: white;'>WAIT!!! THE SEASON IS ABOUT TO START</h2>
            <p style='color: white; font-size: 18px; margin-top: 20px;'>
                The new FPL season hasn't begun yet. Get ready for another exciting season!
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Show welcome to managers
    st.header("👋 Welcome to Our Mini-League Managers!")
    
    # Get league data
    league_data = fetch_data("https://fantasy.premierleague.com/api/leagues-classic/469324/standings/")
    
    managers_info = []
    
    if league_data:
        # During pre-season, check new_entries for manager data
        if 'new_entries' in league_data and 'results' in league_data['new_entries'] and league_data['new_entries']['results']:
            for team in league_data['new_entries']['results']:
                full_name = f"{team['player_first_name']} {team['player_last_name']}"
                managers_info.append({
                    'manager_name': full_name,
                    'team_name': team['entry_name'],
                    'team_link': f"https://fantasy.premierleague.com/entry/{team['entry']}",
                    'entry_id': team['entry']
                })
        
        # If standings has data (during season), use that instead
        elif 'standings' in league_data and 'results' in league_data['standings'] and league_data['standings']['results']:
            for team in league_data['standings']['results']:
                managers_info.append({
                    'manager_name': team['player_name'],
                    'team_name': team['entry_name'],
                    'team_link': f"https://fantasy.premierleague.com/entry/{team['entry']}",
                    'entry_id': team['entry']
                })
    
    if not managers_info:
        st.error("Unable to fetch manager data. Please try again later.")
        return
    
    # Sort managers alphabetically by real name
    managers_info.sort(key=lambda x: x['manager_name'])
    
    # Display managers in a clean grid format with clickable links
    st.markdown("""
        <style>
        .managers-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin: 30px 0;
            padding: 0;
        }
        .manager-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border: none;
            cursor: pointer;
            text-decoration: none;
            display: block;
        }
        .manager-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            text-decoration: none;
            color: white;
        }
        .manager-card:visited {
            color: white;
        }
        .team-name {
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 10px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }
        .real-name {
            font-size: 14px;
            opacity: 0.9;
            font-style: italic;
        }
        .click-hint {
            font-size: 12px;
            opacity: 0.7;
            margin-top: 8px;
        }
        @media (max-width: 768px) {
            .managers-container {
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
            }
            .manager-card {
                padding: 20px;
            }
            .team-name {
                font-size: 20px;
            }
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Create columns for better layout
    cols = st.columns(3)
    
    # Store previous season data for the table
    last_season_stats = []
    
    for i, manager in enumerate(managers_info):
        with cols[i % 3]:
            st.markdown(f"""
                <a href="{manager['team_link']}" target="_blank" class="manager-card">
                    <div class="team-name">{manager['team_name']}</div>
                    <div class="real-name">{manager['manager_name']}</div>
                    <div class="click-hint">Click to view team →</div>
                </a>
            """, unsafe_allow_html=True)
        
        # Get previous season data for this manager
        prev_data = get_previous_season_data(manager.get('entry_id'))
        if prev_data:
            last_season_stats.append({
                'Manager': manager['manager_name'],
                'Team Name': manager['team_name'],
                'Season': prev_data['season'],
                'Total Points': f"{prev_data['total_points']:,}",
                'Overall Rank': f"{prev_data['rank']:,}"
            })
        else:
            last_season_stats.append({
                'Manager': manager['manager_name'],
                'Team Name': manager['team_name'],
                'Season': 'No Data',
                'Total Points': '-',
                'Overall Rank': '-'
            })
    
    # League stats
    league_name = league_data.get('league', {}).get('name', 'Mini-League') if league_data else 'Mini-League'
    st.markdown(
        f"""
        <div style='background-color: #1f1f1f; padding: 20px; border-radius: 10px; text-align: center; margin-top: 30px;'>
            <h3 style='color: #00ff00;'>🏆 {league_name}</h3>
            <p style='color: #cccccc;'>
                <strong>{len(managers_info)} managers</strong> ready to battle it out!
            </p>
            <p style='color: #cccccc; font-style: italic; margin-top: 15px;'>
                🚀 Get ready to plan your squad, set your captains, and chase those green arrows!
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Display Last Season Statistics Table
    if last_season_stats:
        st.header("📊 Last Season Performance")
        
        # Create DataFrame and sort by total points
        df_last_season = pd.DataFrame(last_season_stats)
        
        # Convert Total Points to numeric for sorting (handle '-' values and commas)
        df_last_season['Sort_Points'] = df_last_season['Total Points'].apply(
            lambda x: float(x.replace(',', '')) if x != '-' else 0
        )
        df_last_season = df_last_season.sort_values('Sort_Points', ascending=False)
        
        # Create a clean version for display (without commas for gradient)
        df_display = df_last_season.copy()
        df_display['Points_Numeric'] = df_display['Total Points'].apply(
            lambda x: float(x.replace(',', '')) if x != '-' else 0
        )
        
        # Drop sort columns
        df_display = df_display.drop(['Sort_Points'], axis=1)
        
        # Reset index to show ranking
        df_display.reset_index(drop=True, inplace=True)
        df_display.index += 1  # Start ranking from 1
        
        # Display the table with styling (only apply gradient to numeric column)
        styled_df = df_display.drop('Points_Numeric', axis=1).style.background_gradient(
            subset=['Total Points'], 
            cmap='RdYlGn',
            gmap=df_display['Points_Numeric'].values
        )
        
        st.dataframe(
            styled_df,
            use_container_width=True
        )
        
        # Show some quick stats
        valid_data = [stat for stat in last_season_stats if stat['Total Points'] != '-']
        if valid_data:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                best_manager = max(valid_data, key=lambda x: int(x['Total Points'].replace(',', '')))
                st.metric(
                    "🏆 Last Season Champion", 
                    best_manager['Manager'],
                    f"{best_manager['Total Points']} points"
                )
            
            with col2:
                total_points = [int(d['Total Points'].replace(',', '')) for d in valid_data]
                avg_points = sum(total_points) / len(total_points)
                st.metric("📊 Average Points", f"{avg_points:,.0f}")
            
            with col3:
                seasons = set(d['Season'] for d in valid_data if d['Season'] != 'No Data')
                if seasons:
                    st.metric("📅 Season", list(seasons)[0])
                    
    else:
        st.info("⏳ Loading last season data... This may take a moment.")
        
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-style: italic; margin-top: 20px;'>
            Click on any team card above to view their FPL team page!
        </div>
        """, 
        unsafe_allow_html=True
    )

def get_player_data(bootstrap_data):
    return {p['id']: {
        'name': p['web_name'],
        'position': next(pos['singular_name'] for pos in bootstrap_data['element_types'] 
                        if pos['id'] == p['element_type']),
        'team': next(team['name'] for team in bootstrap_data['teams'] 
                    if team['id'] == p['team'])
    } for p in bootstrap_data['elements']}

def get_detailed_player_info(team_id, event_id, live_data, bootstrap_data, player_data):
    picks = fetch_data(f"https://fantasy.premierleague.com/api/entry/{team_id}/event/{event_id}/picks/")
    if not picks:
        return []
    
    elements_dict = {str(element['id']): element for element in live_data['elements']}
    
    players_info = []
    for pick in picks['picks']:
        player_id = pick['element']
        player_info = player_data[player_id]
        live_stats = elements_dict.get(str(player_id))
        
        if live_stats:
            points = live_stats['stats']['total_points'] * pick['multiplier']
            minutes = live_stats['stats']['minutes']
            
            players_info.append({
                'name': player_info['name'],
                'points': points,
                'is_captain': pick['multiplier'] > 1,
                'position': pick['position'],
                'played': minutes > 0
            })
    
    return sorted(players_info, key=lambda x: x['position'])

def get_manager_gameweek_details(team_id, event_id, live_data, bootstrap_data, player_data):
    picks = fetch_data(f"https://fantasy.premierleague.com/api/entry/{team_id}/event/{event_id}/picks/")
    transfers = fetch_data(f"https://fantasy.premierleague.com/api/entry/{team_id}/transfers/")
    
    if not picks or not transfers:
        return {
            'points_by_position': {'Forward': 0, 'Midfielder': 0, 'Defender': 0, 'Goalkeeper': 0},
            'bench_points': 0,
            'captain_info': None,
            'played_count': 0,
            'transfers_made': 0,
            'transfer_cost': 0,
            'active_chip': None
        }
    
    elements_dict = {str(element['id']): element for element in live_data['elements']}
    
    # Check for Free Hit chip
    is_free_hit = picks.get('active_chip') == 'freehit'
    
    # Get current gameweek transfers and calculate cost
    gw_transfers = [t for t in transfers if t['event'] == event_id]
    # Only apply transfer cost if not using Free Hit
    transfer_cost = 0 if is_free_hit else (len(gw_transfers) * 4 if len(gw_transfers) > 2 else 0)
    
    points_by_position = {'Forward': 0, 'Midfielder': 0, 'Defender': 0, 'Goalkeeper': 0}
    bench_points = 0
    captain_info = None
    played_count = 0
    
    for pick in picks['picks']:
        player_id = pick['element']
        player_info = player_data[player_id]
        live_stats = elements_dict.get(str(player_id))
        
        if live_stats:
            points = live_stats['stats']['total_points'] * pick['multiplier']
            minutes = live_stats['stats']['minutes']
            
            if minutes > 0:
                played_count += 1
            
            if pick['position'] > 11:
                bench_points += points
            else:
                points_by_position[player_info['position']] += points
            
            if pick['multiplier'] > 1:
                captain_info = {
                    'name': player_info['name'],
                    'team': player_info['team'],
                    'points': points,
                    'played': minutes > 0
                }
    
    return {
        'points_by_position': points_by_position,
        'bench_points': bench_points,
        'captain_info': captain_info,
        'played_count': played_count,
        'transfers_made': len(gw_transfers),
        'transfer_cost': transfer_cost,
        'active_chip': picks.get('active_chip')
    }

def show_live_gameweek():
    st.header("🎮 Live Gameweek Dashboard")
    
    bootstrap_data = fetch_data("https://fantasy.premierleague.com/api/bootstrap-static/")
    if not bootstrap_data:
        st.error("Unable to fetch FPL data. Please try again later.")
        return
    
    current_gw = next((event['id'] for event in bootstrap_data['events'] if event['is_current']), 1)
    live_data = fetch_data(f"https://fantasy.premierleague.com/api/event/{current_gw}/live/")
    league_data = fetch_data("https://fantasy.premierleague.com/api/leagues-classic/469324/standings/")
    
    if not live_data or not league_data:
        st.error("Unable to fetch live data or league standings.")
        return
    
    player_data = get_player_data(bootstrap_data)
    
    # Process manager data
    managers_data = []
    detailed_managers_data = []

    for team in league_data['standings']['results']:
        details = get_manager_gameweek_details(
            team['entry'], current_gw, live_data, bootstrap_data, player_data
        )
        
        # Get detailed player information
        players_info = get_detailed_player_info(team['entry'], current_gw, live_data, bootstrap_data, player_data)
        
        # Calculate live points
        live_points = (sum(details['points_by_position'].values()) + 
                      details['bench_points'] - 
                      details['transfer_cost'])
        
        # Data for summary table
        managers_data.append({
            'Manager': team['player_name'],
            'Live Points': live_points,
            'DEF': details['points_by_position']['Defender'],
            'MID': details['points_by_position']['Midfielder'],
            'FWD': details['points_by_position']['Forward'],
            'GK': details['points_by_position']['Goalkeeper'],
        })
        
        # Simplified player HTML without icons, just names and points
        players_html = "<div class='player-list'>"
        for player in players_info:
            # Add (B) for bench, (C) for captain
            suffix = "(B)" if player['position'] > 11 else ""
            suffix += "(C)" if player['is_captain'] else ""
            players_html += f"<span class='player-item'>{player['name']}{suffix}({player['points']})</span>"
        players_html += "</div>"
        
        # Data for detailed table
        detailed_managers_data.append({
            'Manager': f"<a href='https://fantasy.premierleague.com/entry/{team['entry']}/event/{current_gw}' target='_blank'>{team['player_name']}</a>",
            'Players': players_html,
            'Total': live_points,
            'Played': f"{details['played_count']}/11",
            'Transfers': f"{details['transfers_made']} (-{details['transfer_cost']})",
            'Bench': details['bench_points']
        })

    # Create DataFrames
    df_summary = pd.DataFrame(managers_data).sort_values('Live Points', ascending=False)
    df_detailed = pd.DataFrame(detailed_managers_data).sort_values('Total', ascending=False)
    
    # Display current leader
    if not df_summary.empty:
        current_leader = df_summary.iloc[0]
        st.markdown(
            f"""
            <div style='background-color: #1f1f1f; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 30px;'>
                <h2>🏆 Current Gameweek Leader 🏆</h2>
                <h1 style='color: gold; font-size: 48px; margin: 20px 0;'>
                    {current_leader['Manager']}
                </h1>
                <h3 style='color: #00ff00;'>{current_leader['Live Points']} points</h3>
                <p style='font-style: italic; color: #cccccc;'>Gameweek {current_gw}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # CSS for both tables
    st.markdown("""
        <style>
        .table-container {
            margin: 20px 0;
            overflow-x: auto;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background-color: white;
        }
        th {
            background-color: #1f77b4;
            color: white;
            padding: 8px;
            text-align: left;
            position: sticky;
            top: 0;
            z-index: 1;
        }
        td {
            padding: 8px;
            border: 1px solid #ddd;
            vertical-align: middle;
            background-color: white;
            color: black;
        }
        tr:nth-child(even) td {
            background-color: #f5f5f5;
        }
        .player-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            font-size: 12px;
        }
        .player-item {
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            white-space: nowrap;
        }
        @media (max-width: 768px) {
            th, td {
                padding: 4px;
                font-size: 0.85em;
            }
            .player-list {
                font-size: 11px;
                gap: 4px;
            }
            .player-item {
                padding: 1px 2px;
            }
            td[data-row-key="Players"] {
                max-width: 100%;
                overflow-x: auto;
            }
        }
        </style>
    """, unsafe_allow_html=True)

    # Display Summary Table
    if not df_summary.empty:
        st.subheader("📊 Points Summary")
        st.markdown(
            df_summary.style
            .background_gradient(subset=['Live Points', 'DEF', 'MID', 'FWD', 'GK'], cmap='YlOrRd')
            .format({'Live Points': '{:.0f}'})
            .to_html(),
            unsafe_allow_html=True
        )

        # Display Detailed Table
        st.subheader("🎮 Detailed Stats")
        st.markdown(
            df_detailed.style
            .format({'Total': '{:.0f}'})
            .to_html(),
            unsafe_allow_html=True
        )

def show_overall_stats():
    st.header("📊 Overall Statistics")
    
    league_data = fetch_data("https://fantasy.premierleague.com/api/leagues-classic/469324/standings/")
    bootstrap_data = fetch_data("https://fantasy.premierleague.com/api/bootstrap-static/")
    
    if not league_data or not bootstrap_data:
        st.error("Unable to fetch data. Please try again later.")
        return
    
    current_gw = next((event['id'] for event in bootstrap_data['events'] if event['is_current']), 1)
    
    # Process historical data for each manager
    historical_data = []
    weekly_winners = []
    points_matrix = []
    
    for team in league_data['standings']['results']:
        history = fetch_data(f"https://fantasy.premierleague.com/api/entry/{team['entry']}/history/")
        
        if not history or 'current' not in history:
            continue
        
        # Get weekly points
        weekly_points = []
        for gw in history['current']:
            weekly_points.append(gw['points'])
            weekly_winners.append({
                'gameweek': gw['event'],
                'manager': team['player_name'],
                'points': gw['points']
            })
        
        if not weekly_points:
            continue
        
        # Calculate stats
        avg_points = sum(weekly_points)/len(weekly_points)
        std_points = np.std(weekly_points)
        best_week = max(weekly_points)
        worst_week = min(weekly_points)
        
        historical_data.append({
            'Manager': team['player_name'],
            'Total Points': team['total'],
            'Average Points': round(avg_points, 1),
            'Consistency (σ)': round(std_points, 1),
            'Best Week': best_week,
            'Worst Week': worst_week,
            'Current Rank': team['rank']
        })
        
        points_matrix.append(weekly_points)
    
    if not historical_data:
        st.warning("No historical data available yet.")
        return
    
    # Find weekly winners
    df_weekly = pd.DataFrame(weekly_winners)
    if not df_weekly.empty:
        winners_count = df_weekly.groupby(['gameweek', 'manager'])['points'].max()\
                               .reset_index()\
                               .sort_values(['gameweek', 'points'], ascending=[True, False])\
                               .groupby('gameweek').first()\
                               .groupby('manager').size()\
                               .sort_values(ascending=False)
    else:
        winners_count = pd.Series()
    
    # Create heatmap data
    if points_matrix:
        max_gws = max(len(row) for row in points_matrix)
        # Pad shorter rows with None
        padded_matrix = [row + [None] * (max_gws - len(row)) for row in points_matrix]
        
        df_heatmap = pd.DataFrame(padded_matrix, 
                                 index=[d['Manager'] for d in historical_data],
                                 columns=[f'GW{i+1}' for i in range(max_gws)])
    else:
        df_heatmap = pd.DataFrame()
    
    # Display sections
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Overall Leaderboard
        st.subheader("📈 Season Leaderboard")
        df_historical = pd.DataFrame(historical_data)
        st.dataframe(
            df_historical.sort_values('Total Points', ascending=False),
            use_container_width=True
        )
        
        # Points Heatmap
        if not df_heatmap.empty:
            st.subheader("🎯 Points Distribution by Gameweek")
            fig_heatmap = px.imshow(df_heatmap,
                                   labels=dict(x="Gameweek", y="Manager", color="Points"),
                                   aspect='auto',
                                   color_continuous_scale='RdYlGn')
            fig_heatmap.update_layout(height=400)
            st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with col2:
        # Weekly Winners
        if not winners_count.empty:
            st.subheader("🏆 Weekly Winners")
            fig_winners = px.bar(winners_count, 
                               labels={'index': 'Manager', 'value': 'Wins'},
                               title="Number of Weekly Wins")
            st.plotly_chart(fig_winners, use_container_width=True)
        
        # MVP Stats
        st.subheader("🌟 Notable Stats")
        
        if not df_historical.empty:
            # Most Consistent
            most_consistent = df_historical.sort_values('Consistency (σ)').iloc[0]
            st.markdown(f"""
                **Most Consistent Manager**  
                {most_consistent['Manager']} (σ={most_consistent['Consistency (σ)']} pts)
            """)
            
            # Highest Single GW
            highest_gw = df_historical.sort_values('Best Week', ascending=False).iloc[0]
            st.markdown(f"""
                **Highest Single Gameweek**  
                {highest_gw['Manager']} ({highest_gw['Best Week']} pts)
            """)
        
        # Weekly Winners table
        if not winners_count.empty:
            st.markdown("**Weekly Winners**")
            st.dataframe(
                winners_count.reset_index().rename(
                    columns={'index': 'Manager', 0: 'Wins'}
                )
            )

    # Manager comparison section (only if we have data)
    if not df_heatmap.empty:
        st.subheader("📈 Manager Points Comparison")
        
        managers = [d['Manager'] for d in historical_data]
        
        selected_managers = st.multiselect(
            "Select managers to compare",
            options=managers,
            default=managers[:2] if len(managers) >= 2 else managers
        )
        
        if selected_managers:
            comparison_data = df_heatmap.loc[selected_managers]
            
            fig_comparison = go.Figure()
            
            for manager in selected_managers:
                fig_comparison.add_trace(go.Scatter(
                    x=df_heatmap.columns,
                    y=comparison_data.loc[manager],
                    name=manager,
                    mode='lines+markers',
                    hovertemplate="GW%{x}: %{y} points<extra></extra>"
                ))
            
            fig_comparison.update_layout(
                title="Points Progression",
                xaxis_title="Gameweek",
                yaxis_title="Points",
                height=400,
                showlegend=True,
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                ),
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_comparison, use_container_width=True)
            
            # Add statistics table for selected managers
            st.subheader("Comparison Statistics")
            comparison_stats = df_historical[
                df_historical['Manager'].isin(selected_managers)
            ][['Manager', 'Total Points', 'Average Points', 'Consistency (σ)', 
               'Best Week', 'Worst Week', 'Current Rank']]
            
            st.dataframe(
                comparison_stats.sort_values('Total Points', ascending=False),
                use_container_width=True
            )
        else:
            st.warning("Please select at least one manager to view comparison")

def main():
    st.title("⚽ FPL Mini-League Analysis")
    
    # Check if season has started
    bootstrap_data = fetch_data("https://fantasy.premierleague.com/api/bootstrap-static/")
    
    if not bootstrap_data:
        st.error("Unable to connect to FPL API. Please try again later.")
        return
    
    season_started, current_gw = check_season_started(bootstrap_data)
    
    if not season_started:
        show_preseason_message()
        return
    
    # Normal season tabs
    tab1, tab2 = st.tabs(["Live Gameweek", "Overall Statistics"])
    
    with tab1:
        show_live_gameweek()
    
    with tab2:
        show_overall_stats()
    
    # Auto-refresh for live tab
    if st.sidebar.checkbox("Auto-refresh (2 min)", value=True):
        time_since_refresh = (datetime.now() - st.session_state.get('last_refresh', datetime.min)).seconds
        if time_since_refresh >= 120:
            st.session_state.last_refresh = datetime.now()
            st.rerun()

if __name__ == "__main__":
    main()