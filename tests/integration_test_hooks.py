#!/usr/bin/env python3
"""
Test script for Claude Code hooks
"""

import json
import sys
import subprocess


def test_hook(hook_name, test_data):
    """Test a specific hook with test data"""
    print(f"\n=== Testing {hook_name} ===")

    try:
        # Create test input
        test_input = json.dumps(test_data)

        # Run the hook
        process = subprocess.Popen(
            [sys.executable, "-m", "hooks", hook_name],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        stdout, stderr = process.communicate(input=test_input, timeout=30)

        print(f"Exit code: {process.returncode}")
        if stdout:
            print(f"Output: {stdout}")
        if stderr:
            print(f"Errors: {stderr}")

        return process.returncode == 0

    except Exception as e:
        print(f"Test failed: {e}")
        return False


def main():
    """Run hook tests"""
    print("Claude Code Hooks Test Suite")
    print("=" * 40)

    # Test data for different hook types
    test_cases = [
        (
            "PreToolUse",
            {
                "session_id": "test-session",
                "transcript_path": "/tmp/test.jsonl",
                "cwd": "/tmp",
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "ls -la"},
            },
        ),
        (
            "PostToolUse",
            {
                "session_id": "test-session",
                "transcript_path": "/tmp/test.jsonl",
                "cwd": "/tmp",
                "hook_event_name": "PostToolUse",
                "tool_name": "Write",
                "tool_input": {"file_path": "test.py", "content": "print('hello')"},
                "tool_response": {"success": True},
            },
        ),
        (
            "Notification",
            {
                "session_id": "test-session",
                "transcript_path": "/tmp/test.jsonl",
                "cwd": "/tmp",
                "hook_event_name": "Notification",
                "message": "Task completed successfully",
            },
        ),
        (
            "UserPromptSubmit",
            {
                "session_id": "test-session",
                "transcript_path": "/tmp/test.jsonl",
                "cwd": "/tmp",
                "hook_event_name": "UserPromptSubmit",
                "prompt": "Write a function to calculate fibonacci numbers",
            },
        ),
        (
            "Stop",
            {
                "session_id": "test-session",
                "transcript_path": "/tmp/test.jsonl",
                "hook_event_name": "Stop",
                "stop_hook_active": False,
            },
        ),
        (
            "SubagentStop",
            {
                "session_id": "test-session",
                "transcript_path": "/tmp/test.jsonl",
                "hook_event_name": "SubagentStop",
                "stop_hook_active": False,
            },
        ),
        (
            "PreCompact",
            {
                "session_id": "test-session",
                "transcript_path": "/tmp/test.jsonl",
                "hook_event_name": "PreCompact",
                "trigger": "manual",
                "custom_instructions": "",
            },
        ),
        (
            "SessionStart",
            {
                "session_id": "test-session",
                "transcript_path": "/tmp/test.jsonl",
                "hook_event_name": "SessionStart",
                "source": "startup",
            },
        ),
    ]

    # Run tests
    results = []
    for hook_name, test_data in test_cases:
        success = test_hook(hook_name, test_data)
        results.append((hook_name, success))

    # Summary
    print("\n" + "=" * 40)
    print("Test Results:")
    print("=" * 40)

    passed = 0
    for hook_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{hook_name:20} {status}")
        if success:
            passed += 1

    print(f"\nPassed: {passed}/{len(results)}")

    if passed == len(results):
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
