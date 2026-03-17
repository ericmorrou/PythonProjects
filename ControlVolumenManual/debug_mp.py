import mediapipe as mp
import os
import sys

print(f"Python Version: {sys.version}")
print(f"MediaPipe Version: {mp.__version__}")
pkg_path = os.path.dirname(mp.__file__)
print(f"Package Path: {pkg_path}")

print("\n--- File Structure ---")
for root, dirs, files in os.walk(pkg_path):
    level = root.replace(pkg_path, '').count(os.sep)
    indent = ' ' * 4 * level
    print(f'{indent}{os.path.basename(root)}/')
    sub_indent = ' ' * 4 * (level + 1)
    if level < 2: # Don't go too deep
        for f in files[:10]: # Max 10 files per dir
            print(f'{sub_indent}{f}')
        if len(files) > 10:
            print(f'{sub_indent}... ({len(files)-10} more files)')

print("\n--- Testing Imports ---")
try:
    import mediapipe.solutions as s
    print("Import 'mediapipe.solutions' SUCCESS")
except Exception as e:
    print(f"Import 'mediapipe.solutions' FAILED: {e}")

try:
    from mediapipe.python.solutions import hands
    print("Import 'mediapipe.python.solutions.hands' SUCCESS")
except Exception as e:
    print(f"Import 'mediapipe.python.solutions.hands' FAILED: {e}")
