#!/usr/bin/env python3
"""
Debug script to understand anyio and ExceptionGroup issues in container
"""
import sys
import os
import importlib
import traceback

def debug_anyio_installation():
    """Debug anyio installation and dependencies"""
    print("=== ANYIO DEBUGGING ===")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Check if anyio is installed
    try:
        import anyio
        print(f"anyio version: {anyio.__version__}")
        print(f"anyio location: {anyio.__file__}")
    except ImportError as e:
        print(f"anyio import error: {e}")
        return
    
    # Check ExceptionGroup availability
    try:
        from anyio._core._exceptions import ExceptionGroup
        print("✓ ExceptionGroup available in anyio._core._exceptions")
    except ImportError as e:
        print(f"✗ ExceptionGroup import error: {e}")
        
        # Try to see what's in the exceptions module
        try:
            import anyio._core._exceptions as exceptions
            print(f"Available in anyio._core._exceptions: {dir(exceptions)}")
        except Exception as e2:
            print(f"Error inspecting exceptions module: {e2}")
    
    # Check if ExceptionGroup is available in builtins (Python 3.11+)
    try:
        ExceptionGroup  # This should work in Python 3.11+
        print("✓ ExceptionGroup available in builtins")
    except NameError:
        print("✗ ExceptionGroup not available in builtins")
    
    # Check anyio backend imports
    try:
        import anyio._backends._asyncio
        print("✓ anyio._backends._asyncio imports successfully")
    except ImportError as e:
        print(f"✗ anyio._backends._asyncio import error: {e}")
        print(f"Full traceback:")
        traceback.print_exc()

def debug_dependencies():
    """Debug all related dependencies"""
    print("\n=== DEPENDENCY DEBUGGING ===")
    
    # Check key dependencies
    dependencies = [
        'anyio',
        'asyncio',
        'starlette',
        'fastapi',
        'uvicorn'
    ]
    
    for dep in dependencies:
        try:
            module = importlib.import_module(dep)
            if hasattr(module, '__version__'):
                print(f"{dep}: {module.__version__}")
            else:
                print(f"{dep}: installed (no version info)")
        except ImportError as e:
            print(f"{dep}: {e}")

def debug_pip_list():
    """Show installed packages"""
    print("\n=== INSTALLED PACKAGES ===")
    try:
        import subprocess
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"Error running pip list: {e}")

def debug_environment():
    """Debug environment variables"""
    print("\n=== ENVIRONMENT ===")
    relevant_vars = [
        'PYTHONPATH',
        'PYTHON_VERSION',
        'PATH',
        'LD_LIBRARY_PATH'
    ]
    
    for var in relevant_vars:
        value = os.environ.get(var)
        if value:
            print(f"{var}: {value}")
        else:
            print(f"{var}: not set")

if __name__ == "__main__":
    debug_anyio_installation()
    debug_dependencies()
    debug_pip_list()
    debug_environment() 