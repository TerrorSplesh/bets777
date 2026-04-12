from flask import Flask, render_template_string, jsonify, request
import requests
import json
import re
from datetime import datetime

app = Flask(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Cache-Control': 'no-cache',
}

HERO_WIN_RATES_PUB = {
    "Phantom Assassin": 50.4, "Spirit Breaker": 51.9, "Queen of Pain": 50.3,
    "Juggernaut": 51.5, "Faceless Void": 53.3, "Lifestealer": 52.5,
    "Doom": 47.0, "Meepo": 49.4, "Invoker": 53.1, "Tidehunter": 51.6,
    "Chen": 50.7, "Keeper of the Light": 49.1, "Earthshaker": 48.6,
    "Axe": 51.2, "Pudge": 52.0, "Bloodseeker": 50.8, "Shadow Fiend": 51.5,
    "Sniper": 52.3, "Morphling": 51.0, "Mirana": 50.5, "Storm Spirit": 52.8,
    "Anti-Mage": 51.2, "Riki": 50.1, "Slark": 51.5, "Sven": 52.0,
    "Wraith King": 50.3, "Kunkka": 49.5, "Huskar": 48.2, "Drow Ranger": 53.5,
    "Lycan": 48.5, "Luna": 51.8, "Dragon Knight": 49.2, "Medusa": 50.5,
    "Batrider": 51.2, "Clinkz": 50.5, "Bounty Hunter": 52.0, "Ursa": 51.5,
    "Templar Assassin": 52.3, "Nyx Assassin": 53.8, "Visage": 47.5,
    "Silencer": 49.0, "Necrophos": 51.0, "Warlock": 48.5, "Beastmaster": 50.8,
    "Sand King": 51.2, "Enigma": 50.5, "Pugna": 51.0, "Dark Seer": 49.8,
    "Lich": 52.0, "Lion": 51.5, "Witch Doctor": 51.9, "Jakiro": 50.2,
    "Crystal Maiden": 52.5, "Ogre Magi": 51.8, "Skywrath Mage": 50.0,
    "Ancient Apparition": 51.2, "Shadow Shaman": 50.5, "Rubick": 52.0,
    "Disruptor": 50.8, "Oracle": 51.5, "Winter Wyvern": 49.5,
    "Treant Protector": 48.8, "Omniknight": 52.0, "Abaddon": 50.5,
    "Dazzle": 51.0, "Phoenix": 49.2, "Elder Titan": 48.5,
    "Legion Commander": 52.3, "Magnus": 50.8, "Timbersaw": 50.5,
    "Brewmaster": 49.8, "Tusk": 51.2, "Chaos Knight": 52.5,
    "Night Stalker": 51.5, "Slardar": 51.2, "Gyrocopter": 49.5,
    "Hoodwink": 52.8, "Dawnbreaker": 50.2, "Marci": 51.0,
    "Void Spirit": 52.5, "Snapfire": 50.8, "Pangolier": 50.5,
    "Grimstroke": 51.2, "Primal Beast": 49.8, "Spectre": 50.5,
    "Weaver": 51.5, "Phantom Lancer": 58.5, "Ember Spirit": 51.0,
    "Leshrac": 48.5, "Death Prophet": 50.5, "Puck": 51.2,
    "Windranger": 50.8, "Zeus": 52.0, "Lina": 51.5,
    "Enchantress": 48.5, "Nature's Prophet": 50.2, "Arc Warden": 49.5,
}

HERO_WIN_RATES_PRO = {
    "Phantom Assassin": 48.5, "Spirit Breaker": 53.7, "Queen of Pain": 50.3,
    "Juggernaut": 49.2, "Faceless Void": 52.0, "Lifestealer": 48.0,
    "Doom": 52.5, "Meepo": 54.0, "Invoker": 52.5, "Tidehunter": 53.5,
    "Chen": 56.0, "Keeper of the Light": 55.2, "Earthshaker": 52.8,
    "Axe": 51.0, "Pudge": 45.0, "Bloodseeker": 48.5, "Shadow Fiend": 49.0,
    "Sniper": 47.5, "Morphling": 55.5, "Mirana": 51.2, "Storm Spirit": 53.8,
    "Anti-Mage": 54.0, "Riki": 46.5, "Slark": 50.5, "Sven": 53.0,
    "Wraith King": 51.5, "Kunkka": 52.0, "Huskar": 54.5, "Drow Ranger": 49.0,
    "Lycan": 55.0, "Luna": 48.5, "Dragon Knight": 52.5, "Medusa": 51.0,
    "Batrider": 58.5, "Clinkz": 51.0, "Bounty Hunter": 49.5, "Ursa": 47.0,
    "Templar Assassin": 53.0, "Nyx Assassin": 52.5, "Visage": 54.0,
    "Silencer": 53.0, "Necrophos": 52.0, "Warlock": 55.5, "Beastmaster": 56.0,
    "Sand King": 53.5, "Enigma": 57.0, "Pugna": 49.0, "Dark Seer": 55.5,
    "Lich": 50.5, "Lion": 49.5, "Witch Doctor": 51.0, "Jakiro": 52.0,
    "Crystal Maiden": 47.5, "Ogre Magi": 50.5, "Skywrath Mage": 46.0,
    "Ancient Apparition": 52.5, "Shadow Shaman": 51.0, "Rubick": 54.5,
    "Disruptor": 55.0, "Oracle": 53.5, "Winter Wyvern": 54.0,
    "Treant Protector": 56.5, "Omniknight": 50.0, "Abaddon": 49.0,
    "Dazzle": 51.5, "Phoenix": 55.0, "Elder Titan": 55.5,
    "Legion Commander": 51.0, "Magnus": 56.5, "Timbersaw": 52.5,
    "Brewmaster": 57.0, "Tusk": 52.0, "Chaos Knight": 48.5,
    "Night Stalker": 53.5, "Slardar": 52.0, "Gyrocopter": 51.5,
    "Hoodwink": 50.0, "Dawnbreaker": 52.0, "Marci": 48.0,
    "Void Spirit": 54.5, "Snapfire": 51.0, "Pangolier": 53.0,
    "Grimstroke": 54.0, "Primal Beast": 51.5, "Spectre": 52.5,
    "Weaver": 49.5, "Phantom Lancer": 51.0, "Ember Spirit": 53.0,
    "Leshrac": 54.5, "Death Prophet": 52.5, "Puck": 55.0,
    "Windranger": 52.0, "Zeus": 49.0, "Lina": 50.5,
    "Enchantress": 55.5, "Nature's Prophet": 53.0, "Arc Warden": 56.0,
}

HERO_PRO_PICK_RATE = {
    "Batrider": 15.2, "Visage": 8.5, "Chen": 7.8, "Magnus": 12.5,
    "Dark Seer": 9.2, "Enigma": 6.5, "Rubick": 14.0, "Puck": 11.8,
    "Storm Spirit": 10.5, "Templar Assassin": 9.8, "Ember Spirit": 11.2,
    "Void Spirit": 8.8, "Hoodwink": 7.5, "Monkey King": 10.0,
    "Snapfire": 6.2, "Grimstroke": 9.5, "Pangolier": 8.2,
    "Marci": 5.5, "Dawnbreaker": 7.0, "Primal Beast": 6.8,
    "Winter Wyvern": 8.5, "Oracle": 7.2, "Disruptor": 9.0,
    "Phoenix": 8.0, "Legion Commander": 12.0, "Night Stalker": 7.5,
    "Slardar": 8.8, "Brewmaster": 6.5, "Tusk": 7.8,
    "Sand King": 10.2, "Beastmaster": 5.8, "Nature's Prophet": 9.2,
}

def get_hero_winrate(hero_name, mode='both'):
    if not hero_name:
        return 50.0
    
    hero_normalized = hero_name.lower().replace(' ', '').replace('_', '').replace('-', '')
    
    def find_match(db):
        for hr_name, wr in db.items():
            hr_normalized = hr_name.lower().replace(' ', '').replace('_', '').replace('-', '')
            if hero_normalized in hr_normalized or hr_normalized in hero_normalized:
                return wr
        return None
    
    if mode == 'pub':
        return find_match(HERO_WIN_RATES_PUB) or 50.0
    elif mode == 'pro':
        return find_match(HERO_WIN_RATES_PRO) or 50.0
    else:
        pub = find_match(HERO_WIN_RATES_PUB) or 50.0
        pro = find_match(HERO_WIN_RATES_PRO) or 50.0
        return (pub + pro) / 2

def get_hero_pro_strength(hero_name):
    if not hero_name:
        return 50.0
    
    hero_normalized = hero_name.lower().replace(' ', '').replace('_', '').replace('-', '')
    
    for hr_name, wr in HERO_WIN_RATES_PRO.items():
        hr_normalized = hr_name.lower().replace(' ', '').replace('_', '').replace('-', '')
        if hero_normalized in hr_normalized or hr_normalized in hero_normalized:
            pick_rate = HERO_PRO_PICK_RATE.get(hr_name, 5.0)
            return round(wr + (pick_rate * 0.1), 1)
    
    return 50.0

def parse_hawk(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        html = response.text
        
        match = re.search(r'data-page="({.*?})"', html)
        if not match:
            return {"teams": [], "tournament": "Unknown", "picks": {"team1": [], "team2": []}, "series_status": "unknown"}
        
        json_str = match.group(1).replace('&quot;', '"')
        page_data = json.loads(json_str)
        series_data = page_data.get('props', {}).get('seriesPageData', {})
        
        team1_picks = []
        team2_picks = []
        series_status = "unknown"
        current_map_odds = None
        
        if series_data:
            team1_data = series_data.get('team1', {})
            team2_data = series_data.get('team2', {})
            championship = series_data.get('championship', {})
            best_of = series_data.get('bestOf', 3)
            
            team1_score = 0
            team2_score = 0
            matches = series_data.get('matches', [])
            
            for m in matches:
                is_winner = m.get('isTeam1Winner')
                if is_winner is True:
                    team1_score += 1
                elif is_winner is False:
                    team2_score += 1
            
            scoreboard = series_data.get('scoreboard', {})
            live_match = series_data.get('currentMatch', {})
            current_map_score = {'radiant': 0, 'dire': 0}
            
            if team1_score == 0 and team2_score == 0:
                team1_score = scoreboard.get('team1Score', 0) or scoreboard.get('team1Wins', 0) or 0
                team2_score = scoreboard.get('team2Score', 0) or scoreboard.get('team2Wins', 0) or 0
            
            if team1_score == 0 and team2_score == 0:
                team1_score = series_data.get('team1Score', 0) or series_data.get('score', {}).get('team1', 0) or 0
                team2_score = series_data.get('team2Score', 0) or series_data.get('score', {}).get('team2', 0) or 0
            
            if team1_score == 0 and team2_score == 0:
                html_lower = html.lower()
                team1_lower = team1_data.get('name', '').lower()
                team2_lower = team2_data.get('name', '').lower()
                
                score_pattern = r'>(\d+)\s*-\s*(\d+)<'
                match = re.search(score_pattern, html_lower)
                if match:
                    s1 = int(match.group(1))
                    s2 = int(match.group(2))
                    if s1 <= 3 and s2 <= 3:
                        team1_score = s1
                        team2_score = s2
                
                if team1_score == 0 and team2_score == 0:
                    score_pattern2 = r'best\s*of\s*\d+.*?(\d+)\s*[-–]\s*(\d+)|(\d+)\s*[-–]\s*(\d+).*?' + re.escape(team1_lower)
                    match2 = re.search(score_pattern2, html_lower)
                    if match2:
                        g = match2.groups()
                        team1_score = int(g[0] or g[2] or 0)
                        team2_score = int(g[1] or g[3] or 0)
            
            if live_match:
                states = live_match.get('states', [])
                if states:
                    current_map_score['radiant'] = states[-1].get('radiantScore', 0) or 0
                    current_map_score['dire'] = states[-1].get('direScore', 0) or 0
            
            if not team1_picks and not team2_picks and live_match:
                picks = live_match.get('picks', [])
                for pick in picks:
                    hero_name = pick.get('hero', {}).get('name', '')
                    if hero_name:
                        hero_name = hero_name.replace('npc_dota_hero_', '').replace('_', ' ').title()
                        if pick.get('isRadiant'):
                            team1_picks.append(hero_name)
                        else:
                            team2_picks.append(hero_name)
            
            if team1_score > 0 or team2_score > 0:
                completed_maps = team1_score + team2_score
                if completed_maps >= best_of:
                    series_status = "series_finished"
                elif team1_score >= (best_of // 2 + 1) or team2_score >= (best_of // 2 + 1):
                    series_status = "series_finished"
                else:
                    series_status = "map_in_progress"
            else:
                series_status = "no_maps_played"
            
            if matches:
                first_match = matches[-1]
                picks = first_match.get('picks', [])
                
                states = first_match.get('states', [])
                if states:
                    game_time = states[-1].get('gameTime', 0) if states else 0
                    radiant_score = states[-1].get('radiantScore', 0) if states else 0
                    dire_score = states[-1].get('direScore', 0) if states else 0
                    
                    if game_time > 0:
                        series_status = "map_in_progress"
                
                for pick in picks:
                    hero_name = pick.get('hero', {}).get('name', '')
                    if hero_name:
                        hero_name = hero_name.replace('npc_dota_hero_', '').replace('_', ' ').title()
                        if pick.get('isRadiant'):
                            team1_picks.append(hero_name)
                        else:
                            team2_picks.append(hero_name)
            
            odds_data = {}
            all_odds = {}
            
            moneylines = series_data.get('moneylines', [])
            if moneylines:
                for ml in moneylines:
                    provider = ml.get('oddsProviderCodeName', '')
                    t1 = ml.get('team1WinOdds', '')
                    t2 = ml.get('team2WinOdds', '')
                    market = ml.get('marketType', 'map_winner')
                    
                    if t1 and t2:
                        provider_key = provider.replace('-', '').replace('_', '')
                        all_odds[provider] = {'team1': t1, 'team2': t2, 'market': market}
                        
                        if provider == 'ggbet':
                            odds_data['ggbet'] = {'team1': t1, 'team2': t2}
                        elif provider == 'parimatch':
                            odds_data['parimatch'] = {'team1': t1, 'team2': t2}
                        elif provider == 'betboom':
                            odds_data['betboom'] = {'team1': t1, 'team2': t2}
                        elif provider == 'spin-better':
                            odds_data['spinbetter'] = {'team1': t1, 'team2': t2}
            
            map_odds = {}
            series_odds = {}
            odds_paused = {}
            
            if moneylines:
                for ml in moneylines:
                    provider = ml.get('oddsProviderCodeName', '')
                    market = ml.get('marketType', 'map_winner')
                    t1 = ml.get('team1WinOdds', '')
                    t2 = ml.get('team2WinOdds', '')
                    
                    is_suspended = ml.get('isSuspended', False) or ml.get('isPaused', False)
                    
                    if not t1 or not t2 or is_suspended:
                        bm_key = provider.replace('-', '').replace('_', '').replace(' ', '')
                        odds_paused[bm_key] = True
                        continue
                    
                    if market in ['map_winner', 'match_winner']:
                        for bm in ['ggbet', 'parimatch', 'betboom', 'spinbetter']:
                            if bm in provider.lower() or provider.lower() in bm:
                                if market == 'match_winner':
                                    series_odds[bm] = {'team1': t1, 'team2': t2}
                                else:
                                    map_odds[bm] = {'team1': t1, 'team2': t2}
            
            if not odds_data:
                for m in matches:
                    odds_bundles = m.get('oddsBundles', [])
                    
                    for bundle in odds_bundles:
                        provider = bundle.get('oddsProviderCodeName', '')
                        is_team1_first = bundle.get('isTeam1First', True)
                        odds_list = bundle.get('odds', [])
                        
                        for odd_item in reversed(odds_list):
                            t1_raw = odd_item.get('firstTeamWin')
                            t2_raw = odd_item.get('secondTeamWin')
                            
                            if t1_raw and t2_raw:
                                if provider == 'ggbet':
                                    odds_data['ggbet'] = {'team1': t1_raw if is_team1_first else t2_raw, 'team2': t2_raw if is_team1_first else t1_raw}
                                elif provider == 'parimatch':
                                    odds_data['parimatch'] = {'team1': t1_raw if is_team1_first else t2_raw, 'team2': t2_raw if is_team1_first else t1_raw}
                                elif provider == 'betboom':
                                    odds_data['betboom'] = {'team1': t1_raw if is_team1_first else t2_raw, 'team2': t2_raw if is_team1_first else t1_raw}
                                elif provider == 'spin-better':
                                    odds_data['spinbetter'] = {'team1': t1_raw if is_team1_first else t2_raw, 'team2': t2_raw if is_team1_first else t1_raw}
                                break
            
            return {
                "teams": [team1_data.get('name', ''), team2_data.get('name', '')],
                "tournament": championship.get('name', 'Unknown'),
                "picks": {"team1": team1_picks, "team2": team2_picks},
                "series_status": series_status,
                "team1_score": team1_score,
                "team2_score": team2_score,
                "current_map_score": current_map_score,
                "best_of": best_of,
                "current_odds": odds_data if odds_data else None,
                "map_odds": map_odds if map_odds else odds_data,
                "series_odds": series_odds,
                "odds_paused": odds_paused,
                "is_odds_available": bool(odds_data)
            }
        
        return {"teams": [], "tournament": "Unknown", "picks": {"team1": [], "team2": []}, "series_status": "unknown"}
    except Exception as e:
        print(f"Parse error: {e}")
        return {"teams": [], "tournament": "Error", "picks": {"team1": [], "team2": []}, "series_status": "unknown"}

def calculate_team_stats(picks):
    if not picks:
        return {"avg_pub": 50.0, "avg_pro": 50.0, "avg_both": 50.0, "pro_strength": 50.0}
    
    pub_total, pro_total, both_total, pro_strength_total = 0, 0, 0, 0
    count = 0
    
    for hero in picks:
        pub_wr = get_hero_winrate(hero, 'pub')
        pro_wr = get_hero_winrate(hero, 'pro')
        pro_str = get_hero_pro_strength(hero)
        
        pub_total += pub_wr
        pro_total += pro_wr
        both_total += (pub_wr + pro_wr) / 2
        pro_strength_total += pro_str
        count += 1
    
    if count == 0:
        return {"avg_pub": 50.0, "avg_pro": 50.0, "avg_both": 50.0, "pro_strength": 50.0}
    
    return {
        "avg_pub": round(pub_total / count, 1),
        "avg_pro": round(pro_total / count, 1),
        "avg_both": round(both_total / count, 1),
        "pro_strength": round(pro_strength_total / count, 1)
    }

def calculate_advantage(team1_picks, team2_picks):
    if not team1_picks and not team2_picks:
        return 50, 50, {}, {}
    
    t1_stats = calculate_team_stats(team1_picks)
    t2_stats = calculate_team_stats(team2_picks)
    
    diff_pub = t1_stats['avg_pub'] - t2_stats['avg_pub']
    diff_pro = t1_stats['avg_pro'] - t2_stats['avg_pro']
    diff_both = t1_stats['avg_both'] - t2_stats['avg_both']
    diff_strength = t1_stats['pro_strength'] - t2_stats['pro_strength']
    
    combined_diff = (diff_both * 0.4) + (diff_strength * 0.4) + (diff_pro * 0.2)
    
    team1_adv = 50 + combined_diff
    team2_adv = 50 - combined_diff
    
    team1_adv = max(5, min(95, team1_adv))
    team2_adv = 100 - team1_adv
    
    return team1_adv, team2_adv, t1_stats, t2_stats

HTML = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎮 Betting Odds Comparator</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0d0d0d 0%, #1a1a2e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 20px;
        }
        .container { max-width: 950px; margin: 0 auto; }
        h1 {
            font-size: 2.5rem;
            color: #ff6b35;
            text-align: center;
            margin-bottom: 20px;
        }
        .input-container {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        input[type="text"] {
            flex: 1;
            padding: 15px;
            font-size: 16px;
            border: 2px solid #3d3d5c;
            border-radius: 8px;
            background: #1e1e2e;
            color: #fff;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #ff6b35;
        }
        .match-info {
            background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            text-align: center;
        }
        .match-info h2 {
            font-size: 1.8rem;
            margin-bottom: 10px;
        }
        .vs { color: #ff6b35; }
        .tournament { color: #888; font-size: 0.9rem; }
        .score-display {
            font-size: 1.5rem;
            font-weight: bold;
            margin: 10px 0;
        }
        .score-team1 { color: #ff6b35; }
        .score-team2 { color: #6366f1; }
        .map-status {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .status-upcoming { background: #3b82f6; color: #fff; }
        .status-live { background: #22c55e; color: #fff; }
        .status-finished { background: #ef4444; color: #fff; }
        .picks-info {
            margin-top: 15px;
            padding: 10px;
            background: #252540;
            border-radius: 8px;
            font-size: 0.85rem;
        }
        .pick-hero {
            display: inline-block;
            background: #3d3d5c;
            padding: 3px 8px;
            border-radius: 4px;
            margin: 2px;
            font-size: 0.8rem;
        }
        .advantage-bar {
            display: flex;
            height: 40px;
            border-radius: 20px;
            overflow: hidden;
            margin: 15px 0;
            background: #1e1e2e;
        }
        .advantage-team1 {
            background: linear-gradient(90deg, #ff6b35, #ff8f65);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: #fff;
            transition: width 0.5s ease;
        }
        .advantage-team2 {
            background: linear-gradient(90deg, #6366f1, #818cf8);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: #fff;
            transition: width 0.5s ease;
        }
        .advantage-label {
            display: flex;
            justify-content: space-between;
            font-size: 0.9rem;
            color: #888;
            margin-bottom: 10px;
        }
        .stats-row {
            display: flex;
            justify-content: space-between;
            gap: 15px;
            margin-bottom: 15px;
        }
        .stat-card {
            flex: 1;
            background: #1e1e2e;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-title {
            font-size: 0.75rem;
            color: #888;
            margin-bottom: 5px;
        }
        .stat-value {
            font-size: 1.1rem;
            font-weight: bold;
        }
        .stat-pub { color: #4ade80; }
        .stat-pro { color: #f472b6; }
        .stat-combo { color: #fbbf24; }
        table { width: 100%; border-collapse: collapse; }
        th, td {
            padding: 12px;
            text-align: center;
            border-bottom: 1px solid #3d3d5c;
        }
        th { background: #1e1e2e; }
        .odds-closed {
            background: #374151 !important;
            color: #9ca3af !important;
            padding: 5px 15px;
            border-radius: 4px;
            font-weight: bold;
        }
        .odds-paused {
            background: #f59e0b !important;
            color: #000 !important;
            padding: 5px 15px;
            border-radius: 4px;
            font-weight: bold;
        }
        .best-odd {
            background: linear-gradient(135deg, #00c853 0%, #00e676 100%);
            color: #000;
            padding: 5px 15px;
            border-radius: 4px;
            font-weight: bold;
        }
        .update-time {
            text-align: center;
            color: #888;
            margin-top: 20px;
            font-size: 0.9rem;
        }
        .method-info {
            background: #252540;
            padding: 10px;
            border-radius: 8px;
            font-size: 0.8rem;
            color: #aaa;
            margin-bottom: 15px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Betting Odds Comparator</h1>
        
        <div class="input-container">
            <input type="text" id="matchUrl" placeholder="https://hawk.live/dota-2/matches/..." value="{{ match_url }}">
        </div>
        
        <div id="content">
            {% if teams %}
            <div class="match-info">
                <h2>{{ teams[0] }} <span class="vs">VS</span> {{ teams[1] }}</h2>
                <p class="tournament">🏆 {{ tournament }}</p>
                
                <div class="score-display">
                    <span class="score-team1">{{ team1_score }}</span> - <span class="score-team2">{{ team2_score }}</span>
                    <span style="color: #888; font-size: 0.9rem;"> (BO{{ best_of }})</span>
                    {% if current_map_score.radiant or current_map_score.dire %}
                    <span style="color: #888; font-size: 0.8rem; margin-left: 10px;">| Карта: {{ current_map_score.radiant }} - {{ current_map_score.dire }}</span>
                    {% endif %}
                </div>
                
                {% if series_status == 'series_finished' %}
                <span class="map-status status-finished">✅ Серия завершена</span>
                {% elif series_status == 'map_in_progress' %}
                <span class="map-status status-live">🔴 Карта в процессе</span>
                {% else %}
                <span class="map-status status-upcoming">📋 Матч скоро</span>
                {% endif %}
                
                {% if picks.team1 or picks.team2 %}
                <div class="picks-info">
                    <p><strong>{{ teams[0] }}:</strong> {% for hero in picks.team1 %}<span class="pick-hero">{{ hero }}</span>{% endfor %}</p>
                    <p><strong>{{ teams[1] }}:</strong> {% for hero in picks.team2 %}<span class="pick-hero">{{ hero }}</span>{% endfor %}</p>
                </div>
                {% endif %}
            </div>
            
            {% if series_status != 'series_finished' and (team1_advantage > 0 or team2_advantage > 0) %}
            <div class="method-info">
                📊 Метод: Pub Winrate (40%) + Pro Winrate (20%) + Pro Strength (40%)
            </div>
            
            <div class="stats-row">
                <div class="stat-card">
                    <div class="stat-title">{{ teams[0] }} - Pub WR</div>
                    <div class="stat-value stat-pub">{{ team1_stats.avg_pub }}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">{{ teams[0] }} - Pro WR</div>
                    <div class="stat-value stat-pro">{{ team1_stats.avg_pro }}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">{{ teams[0] }} - Combo</div>
                    <div class="stat-value stat-combo">{{ team1_stats.avg_both }}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">{{ teams[0] }} - Pro Strength</div>
                    <div class="stat-value stat-combo">{{ team1_stats.pro_strength }}%</div>
                </div>
            </div>
            
            <div class="stats-row">
                <div class="stat-card">
                    <div class="stat-title">{{ teams[1] }} - Pub WR</div>
                    <div class="stat-value stat-pub">{{ team2_stats.avg_pub }}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">{{ teams[1] }} - Pro WR</div>
                    <div class="stat-value stat-pro">{{ team2_stats.avg_pro }}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">{{ teams[1] }} - Combo</div>
                    <div class="stat-value stat-combo">{{ team2_stats.avg_both }}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">{{ teams[1] }} - Pro Strength</div>
                    <div class="stat-value stat-combo">{{ team2_stats.pro_strength }}%</div>
                </div>
            </div>
            
            <div class="advantage-label">
                <span>{{ teams[0] }} - {{ team1_advantage }}%</span>
                <span>🎯 Перевес пика</span>
                <span>{{ teams[1] }} - {{ team2_advantage }}%</span>
            </div>
            <div class="advantage-bar">
                <div class="advantage-team1" style="width: {{ team1_advantage }}%">{{ team1_advantage }}%</div>
                <div class="advantage-team2" style="width: {{ team2_advantage }}%">{{ team2_advantage }}%</div>
            </div>
            {% endif %}
            
            <table>
                <thead>
                    <tr>
                        <th>Букмекер</th>
                        <th>{{ teams[0] }} (карта)</th>
                        <th>{{ teams[1] }} (карта)</th>
                    </tr>
                </thead>
                <tbody id="oddsTable">
                    {% for bookmaker in bookmakers %}
                    <tr class="odds-row-{{ bookmaker }}">
                        <td><strong>{{ bookmaker }}</strong></td>
                        {% if series_status == 'series_finished' %}
                        <td class="team1-{{ bookmaker }}"><span class="odds-closed">❌ Закрыто</span></td>
                        <td class="team2-{{ bookmaker }}"><span class="odds-closed">❌ Закрыто</span></td>
                        {% elif not is_odds_available %}
                        <td class="team1-{{ bookmaker }}"><span class="odds-closed">❌ Закрыто</span></td>
                        <td class="team2-{{ bookmaker }}"><span class="odds-closed">❌ Закрыто</span></td>
                        {% elif odds_paused.get(bookmaker) or odds_paused.get(bookmaker.replace('-', '').replace(' ', '')) %}
                        <td class="team1-{{ bookmaker }}"><span class="odds-paused">⏸️ Пауза</span></td>
                        <td class="team2-{{ bookmaker }}"><span class="odds-paused">⏸️ Пауза</span></td>
                        {% else %}
                        <td class="team1-{{ bookmaker }}">{{ map_odds.get(bookmaker, {}).get('team1', odds.get(bookmaker, {}).get('team1', 'N/A')) }}</td>
                        <td class="team2-{{ bookmaker }}">{{ map_odds.get(bookmaker, {}).get('team2', odds.get(bookmaker, {}).get('team2', 'N/A')) }}</td>
                        {% endif %}
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            
            {% if series_odds %}
            <h3 style="margin-top: 20px; color: #ff6b35;">🏆 Победа в серии</h3>
            <table>
                <thead>
                    <tr>
                        <th>Букмекер</th>
                        <th>{{ teams[0] }}</th>
                        <th>{{ teams[1] }}</th>
                    </tr>
                </thead>
                <tbody id="seriesOddsTable">
                    {% for bookmaker in bookmakers %}
                    <tr class="series-odds-row-{{ bookmaker }}">
                        <td><strong>{{ bookmaker }}</strong></td>
                        {% if series_status == 'series_finished' or not series_odds.get(bookmaker) %}
                        <td class="team1-series-{{ bookmaker }}"><span class="odds-closed">-</span></td>
                        <td class="team2-series-{{ bookmaker }}"><span class="odds-closed">-</span></td>
                        {% else %}
                        <td class="team1-series-{{ bookmaker }}">{{ series_odds.get(bookmaker, {}).get('team1', '-') }}</td>
                        <td class="team2-series-{{ bookmaker }}">{{ series_odds.get(bookmaker, {}).get('team2', '-') }}</td>
                        {% endif %}
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% endif %}
            
            <p class="update-time">🔄 <span id="updateTime">Обновлено</span></p>
            {% else %}
            <p style="text-align: center; color: #888;">👆 Введите ссылку на матч с Hawk Live</p>
            {% endif %}
        </div>
    </div>
    
    <script>
        let url = document.getElementById('matchUrl').value;
        let interval;
        let lastSeriesStatus = "{{ series_status }}";
        
        if (url) {
            startAutoRefresh();
        }
        
        document.getElementById('matchUrl').addEventListener('change', function() {
            url = this.value;
            if (url) {
                startAutoRefresh();
                window.location.href = '?url=' + encodeURIComponent(url);
            }
        });
        
        function startAutoRefresh() {
            if (interval) clearInterval(interval);
            refreshOdds();
            interval = setInterval(refreshOdds, 3000);
        }
        
        async function refreshOdds() {
            if (!url) return;
            
            try {
                const response = await fetch('/api/odds?url=' + encodeURIComponent(url));
                const data = await response.json();
                
                if (data.odds || data.team1_score !== undefined) {
                    if (data.series_status !== lastSeriesStatus) {
                        lastSeriesStatus = data.series_status;
                        window.location.reload();
                        return;
                    }
                    
                    if (typeof data.team1_score === 'number') {
                        let scoreHtml = '<span class="score-team1">' + data.team1_score + '</span> - <span class="score-team2">' + data.team2_score + '</span><span style="color: #888; font-size: 0.9rem;"> (BO' + data.best_of + ')</span>';
                        if (data.current_map_score && (data.current_map_score.radiant || data.current_map_score.dire)) {
                            scoreHtml += '<span style="color: #888; font-size: 0.8rem; margin-left: 10px;">| Карта: ' + data.current_map_score.radiant + ' - ' + data.current_map_score.dire + '</span>';
                        }
                        const scoreEl = document.querySelector('.score-display');
                        if (scoreEl) {
                            scoreEl.innerHTML = scoreHtml;
                        }
                        
                        const statusEl = document.querySelector('.map-status');
                        if (statusEl) {
                            if (data.series_status === 'series_finished') {
                                statusEl.outerHTML = '<span class="map-status status-finished">✅ Серия завершена</span>';
                            } else if (data.series_status === 'map_in_progress') {
                                statusEl.outerHTML = '<span class="map-status status-live">🔴 Карта в процессе</span>';
                            } else {
                                statusEl.outerHTML = '<span class="map-status status-upcoming">📋 Матч скоро</span>';
                            }
                        }
                    }
                    
                    updateOddsTable(data.map_odds || data.odds, data.series_status, data.is_odds_available, data.odds_paused || {});
                    updateSeriesOddsTable(data.series_odds, data.series_status);
                    document.getElementById('updateTime').textContent = '🔄 Обновлено: ' + data.time;
                }
            } catch (e) {
                console.error(e);
            }
        }
        
        function updateOddsTable(odds, seriesStatus, isOddsAvailable, oddsPaused = {}) {
            const bookmakers = ['ggbet', 'parimatch', 'betboom', 'spinbetter', 'pinnacle', 'fonbet', 'ray4bet', 'bet365'];
            
            bookmakers.forEach(bm => {
                const el1 = document.querySelector('.team1-' + bm);
                const el2 = document.querySelector('.team2-' + bm);
                const isPaused = oddsPaused[bm] || oddsPaused[bm.replace(/-/g, '').replace(/ /g, '')];
                
                if (seriesStatus === 'series_finished' || !isOddsAvailable) {
                    if (el1) {
                        el1.innerHTML = '<span class="odds-closed">❌ Закрыто</span>';
                        el2.innerHTML = '<span class="odds-closed">❌ Закрыто</span>';
                    }
                } else if (isPaused) {
                    if (el1) {
                        el1.innerHTML = '<span class="odds-paused">⏸️ Пауза</span>';
                        el2.innerHTML = '<span class="odds-paused">⏸️ Пауза</span>';
                    }
                } else if (odds && odds[bm] && odds[bm].team1 && odds[bm].team2) {
                    if (el1) {
                        el1.innerHTML = odds[bm].team1;
                    }
                    if (el2) {
                        el2.innerHTML = odds[bm].team2;
                    }
                } else {
                    if (el1) {
                        el1.innerHTML = '<span class="odds-closed">❌ Закрыто</span>';
                        el2.innerHTML = '<span class="odds-closed">❌ Закрыто</span>';
                    }
                }
            });
        }
        
        function updateSeriesOddsTable(seriesOdds, seriesStatus) {
            const bookmakers = ['ggbet', 'parimatch', 'betboom', 'spinbetter', 'pinnacle', 'fonbet', 'ray4bet', 'bet365'];
            
            bookmakers.forEach(bm => {
                const el1 = document.querySelector('.team1-series-' + bm);
                const el2 = document.querySelector('.team2-series-' + bm);
                
                if (seriesStatus === 'series_finished') {
                    if (el1) {
                        el1.innerHTML = '-';
                        el2.innerHTML = '-';
                    }
                } else if (seriesOdds && seriesOdds[bm] && seriesOdds[bm].team1 && seriesOdds[bm].team2) {
                    if (el1) {
                        el1.innerHTML = seriesOdds[bm].team1;
                    }
                    if (el2) {
                        el2.innerHTML = seriesOdds[bm].team2;
                    }
                }
            });
        }
        
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('url')) {
            document.getElementById('matchUrl').value = urlParams.get('url');
        }
    </script>
</body>
</html>
'''

BOOKMAKERS = ["ggbet", "parimatch", "betboom", "spinbetter", "pinnacle", "fonbet", "ray4bet", "bet365"]

@app.route('/')
def home():
    match_url = request.args.get('url', '')
    teams_data = parse_hawk(match_url) if match_url else {"teams": [], "tournament": "", "picks": {"team1": [], "team2": []}, "series_status": "unknown", "team1_score": 0, "team2_score": 0, "best_of": 3, "current_odds": None}
    
    odds = teams_data.get('current_odds', {}) if match_url else {}
    
    team1_adv, team2_adv, t1_stats, t2_stats = calculate_advantage(
        teams_data.get('picks', {}).get('team1', []),
        teams_data.get('picks', {}).get('team2', [])
    )
    
    return render_template_string(HTML, 
        match_url=match_url,
        teams=teams_data.get('teams', []),
        tournament=teams_data.get('tournament', ''),
        picks=teams_data.get('picks', {'team1': [], 'team2': []}),
        odds=odds,
        map_odds=teams_data.get('map_odds', {}),
        series_odds=teams_data.get('series_odds', {}),
        odds_paused=teams_data.get('odds_paused', {}),
        is_odds_available=teams_data.get('is_odds_available', False),
        bookmakers=BOOKMAKERS,
        team1_advantage=team1_adv,
        team2_advantage=team2_adv,
        team1_stats=t1_stats,
        team2_stats=t2_stats,
        series_status=teams_data.get('series_status', 'unknown'),
        team1_score=teams_data.get('team1_score', 0),
        team2_score=teams_data.get('team2_score', 0),
        current_map_score=teams_data.get('current_map_score', {'radiant': 0, 'dire': 0}),
        best_of=teams_data.get('best_of', 3)
    )

@app.route('/api/odds')
def api_odds():
    match_url = request.args.get('url', '')
    if not match_url:
        return jsonify({"error": "No URL"})
    
    teams_data = parse_hawk(match_url)
    odds = teams_data.get('current_odds', {})
    
    team1_adv, team2_adv, t1_stats, t2_stats = calculate_advantage(
        teams_data.get('picks', {}).get('team1', []),
        teams_data.get('picks', {}).get('team2', [])
    )
    
    return jsonify({
        "teams": teams_data.get('teams', []),
        "tournament": teams_data.get('tournament', ''),
        "picks": teams_data.get('picks', {'team1': [], 'team2': []}),
        "odds": odds,
        "map_odds": teams_data.get('map_odds', {}),
        "series_odds": teams_data.get('series_odds', {}),
        "odds_paused": teams_data.get('odds_paused', {}),
        "is_odds_available": teams_data.get('is_odds_available', False),
        "team1_advantage": team1_adv,
        "team2_advantage": team2_adv,
        "team1_stats": t1_stats,
        "team2_stats": t2_stats,
        "series_status": teams_data.get('series_status', 'unknown'),
        "team1_score": teams_data.get('team1_score', 0),
        "team2_score": teams_data.get('team2_score', 0),
        "current_map_score": teams_data.get('current_map_score', {'radiant': 0, 'dire': 0}),
        "best_of": teams_data.get('best_of', 3),
        "time": datetime.now().strftime("%H:%M:%S")
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
