#!/usr/bin/env python3
"""
Simple test script to check if all imports work correctly for Streamlit Cloud deployment
Run this before deploying to catch import errors
"""

import sys
import traceback

def test_imports():
    """Test all required imports"""
    results = {}
    
    # Core dependencies
    try:
        import streamlit as st
        results['streamlit'] = "✅ OK"
    except ImportError as e:
        results['streamlit'] = f"❌ FAIL: {e}"
    
    try:
        import psutil
        results['psutil'] = "✅ OK"
    except ImportError as e:
        results['psutil'] = f"❌ FAIL: {e}"
    
    try:
        import requests
        results['requests'] = "✅ OK"
    except ImportError as e:
        results['requests'] = f"❌ FAIL: {e}"
    
    try:
        import PIL
        results['pillow'] = "✅ OK"
    except ImportError as e:
        results['pillow'] = f"❌ FAIL: {e}"
    
    try:
        import numpy
        results['numpy'] = "✅ OK"
    except ImportError as e:
        results['numpy'] = f"❌ FAIL: {e}"
    
    try:
        import pandas
        results['pandas'] = "✅ OK"
    except ImportError as e:
        results['pandas'] = f"❌ FAIL: {e}"
    
    # Optional dependencies (should be OK if they fail)
    try:
        import pyttsx3
        results['pyttsx3 (optional)'] = "✅ Available"
    except ImportError:
        results['pyttsx3 (optional)'] = "ℹ️ Not available (OK for cloud)"
    
    try:
        import speech_recognition
        results['speech_recognition (optional)'] = "✅ Available"
    except ImportError:
        results['speech_recognition (optional)'] = "ℹ️ Not available (OK for cloud)"
    
    try:
        import pyaudio
        results['pyaudio (optional)'] = "✅ Available"
    except ImportError:
        results['pyaudio (optional)'] = "ℹ️ Not available (OK for cloud)"
    
    return results

def test_ai_core():
    """Test AI core functionality"""
    try:
        from ai_core import handle_task, llm_fallback
        return "✅ AI core imports successful"
    except ImportError as e:
        return f"❌ AI core import failed: {e}"
    except Exception as e:
        return f"⚠️ AI core import warning: {e}"

def test_app():
    """Test main app imports"""
    try:
        # Import without running
        import app
        return "✅ Main app imports successful"
    except ImportError as e:
        return f"❌ Main app import failed: {e}"
    except Exception as e:
        return f"⚠️ Main app import warning: {e}"

def main():
    print("🧪 Testing Tejas AI Streamlit Deployment Compatibility")
    print("=" * 60)
    
    print("\n📦 Testing Required Dependencies:")
    import_results = test_imports()
    for package, result in import_results.items():
        print(f"  {package}: {result}")
    
    print(f"\n🤖 Testing AI Core:")
    ai_result = test_ai_core()
    print(f"  {ai_result}")
    
    print(f"\n📱 Testing Main App:")
    app_result = test_app()
    print(f"  {app_result}")
    
    print(f"\n🐍 Python Version:")
    print(f"  Python {sys.version}")
    
    # Check for critical failures
    critical_failures = [result for result in import_results.values() if "❌ FAIL" in result]
    
    print("\n" + "=" * 60)
    if critical_failures:
        print("❌ DEPLOYMENT WILL FAIL - Critical dependencies missing:")
        for failure in critical_failures:
            print(f"  {failure}")
        print("\n💡 Fix these issues before deploying to Streamlit Cloud")
        return False
    else:
        print("✅ DEPLOYMENT READY - All critical dependencies available!")
        print("💡 Optional dependencies (audio) may not work in cloud, but that's OK")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)