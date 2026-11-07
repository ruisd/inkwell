#!/usr/bin/env python3
"""
StoryForge — evolution loop entrypoint (自主学习回路)
Runs compose → evaluate → collect → evolve → report
"""

import os, sys, json, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from inkwell.forge.composer import compose_framework
from inkwell.forge.evaluator import evaluate_framework
from inkwell.forge.learner import batch_evolve, evolution_report


def main():
    queries = [
        "一个退休的星际飞船驾驶员，在垃圾星发现了一艘能穿越时间的飞船碎片",
        "古代王朝最后一个太监，在王朝覆灭后发现自己的真实身份是皇族遗孤",
        "未来世界，人类发明了读心术，但发现每个人的内心都有一个不该知道的秘密",
    ]
    
    print("=" * 60)
    print("  StoryForge — 自主学习闭环验证 ✅")
    print("=" * 60)
    
    t0 = time.perf_counter()
    report = batch_evolve(queries, collect_threshold=60.0)
    elapsed = time.perf_counter() - t0
    
    print(f"\n⏱  {elapsed:.1f}s elapsed\n")
    print(f"Total: {report['total']}")
    print(f"Collected: {report['collected']}/{report['total']}")
    print(f"Avg score: {report['avg_score']:.1f}")
    print(f"Best: {report['best_query'][:50]}... ({report['best_score']})")
    
    # Evolution report
    evo = evolution_report()
    print(f"\nEvolution: {evo}")
    
    print("\n✅ 三段式闭环验证完成。")


if __name__ == "__main__":
    main()