#!/usr/bin/env python3
"""
Debug script to test anyio installation and ExceptionGroup import
"""
import sys
import importlib

def test_anyio_installation():
    print("=== anyio Installation Debug ===")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    try:
        import anyio
        print(f"anyio version: {anyio.__version__}")
        print(f"anyio location: {anyio.__file__}")
    except ImportError as e:
        print(f"Failed to import anyio: {e}")
        return False
    
    try:
        from anyio._core._exceptions import ExceptionGroup
        print("✅ Successfully imported ExceptionGroup from anyio._core._exceptions")
    except ImportError as e:
        print(f"❌ Failed to import ExceptionGroup: {e}")
        return False
    
    try:
        from anyio._backends._asyncio import ExceptionGroup as BaseExceptionGroup
        print("✅ Successfully imported ExceptionGroup from anyio._backends._asyncio")
    except ImportError as e:
        print(f"❌ Failed to import ExceptionGroup from _asyncio: {e}")
        return False
    
    return True

def test_builtin_exception_group():
    print("\n=== Builtin ExceptionGroup Test ===")
    try:
        from builtins import ExceptionGroup
        print("✅ Builtin ExceptionGroup available")
    except ImportError:
        print("❌ Builtin ExceptionGroup not available")
        return False
    return True

def test_anyio_backends():
    print("\n=== anyio Backends Test ===")
    try:
        import anyio
        backends = anyio._core._eventloop._BACKENDS
        print(f"Available backends: {list(backends.keys())}")
        
        if 'asyncio' in backends:
            print("✅ asyncio backend available")
        else:
            print("❌ asyncio backend not available")
            
    except Exception as e:
        print(f"❌ Error testing backends: {e}")
        return False
    return True

if __name__ == "__main__":
    print("Starting anyio debug...")
    
    anyio_ok = test_anyio_installation()
    builtin_ok = test_builtin_exception_group()
    backends_ok = test_anyio_backends()
    
    print(f"\n=== Summary ===")
    print(f"anyio installation: {'✅' if anyio_ok else '❌'}")
    print(f"builtin ExceptionGroup: {'✅' if builtin_ok else '❌'}")
    print(f"anyio backends: {'✅' if backends_ok else '❌'}")
    
    if not anyio_ok or not builtin_ok or not backends_ok:
        sys.exit(1)
    else:
        print("✅ All tests passed!") 