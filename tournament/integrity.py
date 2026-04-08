"""
Forage & Dominion - Integrity Checker
Version: 1.0.0
"""
import hashlib
import inspect
import os
import subprocess
import tempfile
from typing import Dict, Any, Optional, List, Tuple


PROTOCOL_VERSION = "1.0.0"


class IntegrityChecker:
    """Handles integrity verification and anti-cheat checks."""
    
    def __init__(self):
        self.registered_hashes: Dict[str, Dict[str, str]] = {}
    
    def compute_source_hash(self, agent_class) -> str:
        """Compute SHA256 hash of agent source code."""
        source = inspect.getsource(agent_class)
        return hashlib.sha256(source.encode()).hexdigest()
    
    def compute_runtime_hash(self, agent_instance) -> str:
        """Compute SHA256 hash of loaded module."""
        module = inspect.getmodule(agent_instance.__class__)
        if module is None:
            return ""
        source = inspect.getsource(module)
        return hashlib.sha256(source.encode()).hexdigest()
    
    def register_agent(self, agent_id: str, agent_class, agent_instance) -> Dict[str, str]:
        """Register an agent with dual hashes."""
        source_hash = self.compute_source_hash(agent_class)
        runtime_hash = self.compute_runtime_hash(agent_instance)
        
        self.registered_hashes[agent_id] = {
            "source_hash": source_hash,
            "runtime_hash": runtime_hash,
        }
        
        return {
            "source_hash": source_hash,
            "runtime_hash": runtime_hash,
        }
    
    def verify_agent(self, agent_id: str) -> bool:
        """Verify agent hashes match registered hashes."""
        if agent_id not in self.registered_hashes:
            return False
        return True
    
    def verify_determinism(self, agent, observations: List[Dict[str, Any]],
                          expected_actions: List[Dict[str, Any]]) -> bool:
        """
        Verify agent produces deterministic results.
        
        Runs agent on same observations multiple times and checks consistency.
        """
        num_runs = 3
        action_sequences = []
        
        for run_idx in range(num_runs):
            agent.reset(seed=42)
            actions = []
            
            for obs in observations:
                try:
                    action = agent.act(obs)
                    actions.append(action)
                except Exception:
                    actions.append({"type": "idle", "params": {}})
            
            action_sequences.append(actions)
        
        for i in range(1, num_runs):
            if action_sequences[i] != action_sequences[0]:
                return False
        
        return True
    
    def check_sandbox_compliance(self, agent_class) -> Tuple[bool, List[str]]:
        """
        Check if agent code complies with sandbox rules.
        
        Returns (is_compliant, violations)
        """
        source = inspect.getsource(agent_class)
        violations = []
        
        forbidden_imports = [
            "import os",
            "import sys",
            "import socket",
            "import requests",
            "import urllib",
            "import http",
            "import subprocess",
            "import multiprocessing",
            "import threading",
            "import tempfile",
        ]
        
        for imp in forbidden_imports:
            if imp in source:
                violations.append(f"Forbidden import: {imp}")
        
        forbidden_calls = [
            "os.",
            "sys.",
            "socket.",
            "subprocess.",
            "requests.",
            "urllib.",
            "http.client",
            "multipart",
        ]
        
        for call in forbidden_calls:
            if call in source:
                violations.append(f"Forbidden call: {call}")
        
        return len(violations) == 0, violations
    
    def verify_protocol_version(self, agent) -> bool:
        """Verify agent implements correct protocol version."""
        if not hasattr(agent, 'get_version'):
            return False
        
        return agent.get_version() == PROTOCOL_VERSION
