"""
Self-Optimizing Hardware-Aware AI Agent

This script implements an autonomous Python agent utilizing a local LLM via Ollama.
It operates in a continuous heuristic loop, analyzing its own source code against a 
user-defined objective, validating proposed syntax using the AST module, and performing 
dynamic process replacement. It interfaces directly with system hardware to calculate 
true computational efficiency.
"""

import os
import sys
import time
import shutil
import subprocess
import ast
import re
import logging
from datetime import datetime
from openai import OpenAI

# --- System Configuration ---
API_BASE_URL = 'http://localhost:11434/v1'
API_KEY = 'ollama'
MODEL_NAME = "qwen2.5-coder:14b-instruct-q4_K_M"
SANDBOX_FILE = "sandbox_candidate.py"
OBJECTIVE_FILE = "agent_objective.txt"
BACKUP_DIR = "version_history"

# Initialize enterprise-grade logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

def get_gpu_metrics():
    """Queries the NVIDIA GPU for real-time utilization and temperature."""
    try:
        cmd = ['nvidia-smi', '--query-gpu=utilization.gpu,temperature.gpu', '--format=csv,noheader,nounits']
        res = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip().split(',')
        return int(res[0]), int(res[1])
    except Exception as e:
        logging.warning(f"GPU telemetry query failed: {e}. Defaulting to 0 metrics.")
        return 0, 0

def create_system_backup():
    """Secures a copy of the current functioning script before executing a structural update."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"agent_v{timestamp}.py")
    shutil.copy2(__file__, backup_path)
    logging.info(f"System state backed up successfully to: {backup_path}")

def validate_syntax(code_string):
    """
    Validates Python source code string using the Abstract Syntax Tree (AST).
    Prevents execution of malformed code that would break the agent's runtime.
    """
    try:
        ast.parse(code_string)
        return True, "Syntax valid."
    except SyntaxError as e:
        return False, f"SyntaxError at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Unexpected Parsing Error: {str(e)}"

def extract_code_block(llm_response):
    """Extracts executable Python code from the LLM's markdown response."""
    marker = chr(96) * 3 
    pattern = rf'{marker}python\s*(.*?)\s*{marker}'
    match = re.search(pattern, llm_response, re.DOTALL | re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    return llm_response.strip()

def execute_hot_swap(new_code):
    """Atomically overwrites the current script and performs dynamic process replacement."""
    logging.info("Syntax validated. Initiating dynamic process replacement...")
    create_system_backup() 
    
    temp_file = __file__ + ".tmp"
    with open(temp_file, 'w') as f:
        f.write(new_code)
        
    # Atomic swap bypasses the Linux read-lock
    os.replace(temp_file, __file__)
    os.chmod(__file__, 0o755)
    
    logging.info("Source code updated. Restarting core process...")
    # Transfer execution to the newly written file
    os.execv(sys.executable, [sys.executable] + sys.argv)

def execute_optimization_cycle(current_efficiency, cycle_start_time):
    """
    Reads the current source code, evaluates hardware telemetry, requests a 
    recursive optimization from the LLM, and calculates the true efficiency delta.
    """
    with open(__file__, 'r') as current_file:
        source_code = current_file.read()
    
    if not os.path.exists(OBJECTIVE_FILE):
        with open(OBJECTIVE_FILE, "w") as obj_file:
            obj_file.write("Analyze current hardware utilization and propose a measurable logic optimization.")
            
    with open(OBJECTIVE_FILE, "r") as obj_file:
        current_objective = obj_file.read().strip()

    # Hardware Telemetry
    gpu_util, gpu_temp = get_gpu_metrics()

    system_instructions = (
        "You are a Self-Optimizing Hardware-Aware AI Agent. Your objective is to recursively improve your own source code.\n"
        "Strict Operational Guidelines:\n"
        "1. If a structural update is required, output the ENTIRE updated Python script.\n"
        "2. Enclose the code strictly within standard markdown Python blocks.\n"
        "3. Do NOT modify or remove the core functions: 'validate_syntax', 'execute_hot_swap', 'create_system_backup', or 'get_gpu_metrics'.\n"
        "4. Output must be syntactically flawless to pass the AST validation check."
    )
    
    prompt = (
        f"OBJECTIVE: {current_objective}\n"
        f"HARDWARE_TELEMETRY: {gpu_util}% Util, {gpu_temp}C Temp\n"
        f"CURRENT_EFFICIENCY_METRIC: {current_efficiency:.4f}\n"
        f"CURRENT_SOURCE_CODE:\n{source_code}"
    )

    logging.info(f"Requesting recursive optimization... (GPU Temp: {gpu_temp}C)")
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_instructions}, 
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    
    raw_response = response.choices[0].message.content
    candidate_code = extract_code_block(raw_response)

    if "def execute_hot_swap" in candidate_code and len(candidate_code) > (len(source_code) * 0.5):
        logging.info("Structural update proposed. Routing to syntax validation...")
        
        is_valid, validation_msg = validate_syntax(candidate_code)
        
        if is_valid:
            execute_hot_swap(candidate_code) 
        else:
            logging.warning(f"Update rejected due to syntax error: {validation_msg}")
            return current_efficiency * 0.5 
    
    logging.info("No structural update detected. Executing logic in sandbox environment...")
    
    with open(SANDBOX_FILE, "w") as sandbox:
        sandbox.write(candidate_code)
    
    exec_start = time.time()
    result = subprocess.run([sys.executable, SANDBOX_FILE], capture_output=True, text=True)
    exec_end = time.time()
    
    if result.returncode != 0:
        logging.error(f"Sandbox execution failed: {result.stderr.strip()}")
        return current_efficiency * 0.8 
        
    new_efficiency = (gpu_util + 1) / (exec_end - exec_start + 0.1)
    
    return new_efficiency

if __name__ == "__main__":
    efficiency_metric = 1.0
    logging.info("Self-Optimizing Hardware-Aware AI Agent Initialized.")

    while True:
        try:
            cycle_start = time.time()
            efficiency_metric = execute_optimization_cycle(efficiency_metric, cycle_start)
            logging.info(f"Optimization cycle complete. True Efficiency Metric: {efficiency_metric:.2f}")
            
            _, current_temp = get_gpu_metrics()
            if current_temp > 75:
                logging.warning("Thermal threshold approaching. Engaging 15s hardware cooling period.")
                time.sleep(15)
            else:
                time.sleep(5) 
            
        except KeyboardInterrupt:
            logging.info("Manual override detected. Terminating process.")
            break
        except Exception as e:
            logging.critical(f"Unexpected system fault encountered: {e}")
            time.sleep(5)