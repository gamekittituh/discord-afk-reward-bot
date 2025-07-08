#!/usr/bin/env python3
"""
Test script for Discord AFK Reward Bot functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot import (
    load_afk_data, save_afk_data, load_rank_config,
    calculate_exp_reward, get_user_rank, format_duration
)
import json
from datetime import datetime, timezone

def test_data_loading():
    """Test data loading functions"""
    print("Testing data loading...")
    
    # Test AFK data loading
    afk_data = load_afk_data()
    assert 'afk_users' in afk_data
    assert 'user_exp' in afk_data
    print("✓ AFK data loading works")
    
    # Test rank config loading
    rank_config = load_rank_config()
    assert 'ranks' in rank_config
    assert 'exp_rate' in rank_config
    print("✓ Rank config loading works")

def test_exp_calculation():
    """Test EXP reward calculation"""
    print("\nTesting EXP calculation...")
    
    # Test different durations
    test_cases = [
        (1, 1),      # 1 minute = 1 EXP
        (30, 30),    # 30 minutes = 30 EXP
        (60, 60),    # 60 minutes = 60 EXP
        (120, 100),  # 120 minutes = 100 EXP (capped)
    ]
    
    for duration_minutes, expected_exp in test_cases:
        actual_exp = calculate_exp_reward(duration_minutes)
        assert actual_exp == expected_exp, f"Expected {expected_exp}, got {actual_exp} for {duration_minutes} minutes"
        print(f"✓ {duration_minutes} minutes = {actual_exp} EXP")

def test_rank_system():
    """Test rank calculation"""
    print("\nTesting rank system...")
    
    test_cases = [
        (0, "Newbie"),
        (50, "Newbie"),
        (100, "Regular"),
        (500, "Active"),
        (1500, "Veteran"),
        (3000, "Expert"),
        (5000, "Master"),
        (10000, "Legend"),
        (99999, "Legend"),  # Should still be Legend
    ]
    
    for exp, expected_rank_name in test_cases:
        rank = get_user_rank(exp)
        assert rank['name'] == expected_rank_name, f"Expected {expected_rank_name}, got {rank['name']} for {exp} EXP"
        print(f"✓ {exp} EXP = {rank['name']}")

def test_duration_formatting():
    """Test duration formatting"""
    print("\nTesting duration formatting...")
    
    test_cases = [
        (30, "30 seconds"),
        (60, "1 minute"),
        (90, "1 minute"),
        (120, "2 minutes"),
        (3600, "1 hour"),
        (3660, "1 hour and 1 minute"),
        (7320, "2 hours and 2 minutes"),
        (7200, "2 hours"),
    ]
    
    for seconds, expected in test_cases:
        actual = format_duration(seconds)
        assert actual == expected, f"Expected '{expected}', got '{actual}' for {seconds} seconds"
        print(f"✓ {seconds}s = '{actual}'")

def test_data_persistence():
    """Test data saving and loading"""
    print("\nTesting data persistence...")
    
    # Create test data
    test_data = {
        "afk_users": {
            "123456": {
                "message": "Test AFK message",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "user_name": "TestUser"
            }
        },
        "user_exp": {
            "123456": 150
        }
    }
    
    # Save test data
    save_afk_data(test_data)
    
    # Load and verify
    loaded_data = load_afk_data()
    assert loaded_data['afk_users']['123456']['message'] == "Test AFK message"
    assert loaded_data['user_exp']['123456'] == 150
    
    # Clean up - restore original empty data
    original_data = {"afk_users": {}, "user_exp": {}}
    save_afk_data(original_data)
    
    print("✓ Data persistence works")

def run_all_tests():
    """Run all tests"""
    print("Running Discord AFK Reward Bot tests...\n")
    
    try:
        test_data_loading()
        test_exp_calculation()
        test_rank_system()
        test_duration_formatting()
        test_data_persistence()
        
        print("\n🎉 All tests passed!")
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)