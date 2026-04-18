"""
test_chatbot.py — Runs all 15 required test questions and logs results
Usage: python test_chatbot.py
Output: test_results.txt
"""

import datetime
from query import get_answer

TEST_QUESTIONS = [
    # Academics
    ("Academics", "When is the last day to drop a class?"),
    ("Academics", "When do finals start?"),
    ("Academics", "What are the graduation application deadlines?"),
    ("Academics", "How do I register for classes?"),
    ("Academics", "What is the academic integrity policy?"),
    # Campus Life
    ("Campus Life", "What dining halls are on campus?"),
    ("Campus Life", "Where is the tutoring center?"),
    ("Campus Life", "What is FAU's policy on alcohol on campus?"),
    ("Campus Life", "Can I use a VPN to access campus resources remotely?"),
    ("Campus Life", "What is FAU's tobacco policy?"),
    # Deadlines & Policies
    ("Deadlines & Policies", "When is tuition due?"),
    ("Deadlines & Policies", "What do I do if I receive a phishing email?"),
    ("Deadlines & Policies", "Can I store student data in Google Drive?"),
    ("Deadlines & Policies", "What is FAU's policy on weapons on campus?"),
    ("Deadlines & Policies", "Who do I contact to report a security incident?"),
]


def run_tests():
    results = []
    print("PolicyOwl — Full Test Suite")
    print("=" * 60)

    for i, (category, question) in enumerate(TEST_QUESTIONS, 1):
        print(f"\n[{i}/15] [{category}]")
        print(f"Q: {question}")
        try:
            answer, sources = get_answer(question)
            status = "OK" if answer and "don't have that information" not in answer else "NO_DATA"
        except Exception as e:
            answer = f"ERROR: {e}"
            sources = []
            status = "ERROR"

        print(f"Status: {status}")
        print(f"A: {answer[:300]}{'...' if len(answer) > 300 else ''}")
        print(f"Sources: {', '.join(sources) if sources else 'none'}")

        results.append({
            "num": i,
            "category": category,
            "question": question,
            "answer": answer,
            "sources": sources,
            "status": status,
        })

    # Write results to file
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open("test_results.txt", "w", encoding="utf-8") as f:
        f.write(f"PolicyOwl Test Results — {timestamp}\n")
        f.write("=" * 60 + "\n\n")

        ok = sum(1 for r in results if r["status"] == "OK")
        no_data = sum(1 for r in results if r["status"] == "NO_DATA")
        errors = sum(1 for r in results if r["status"] == "ERROR")
        f.write(f"SUMMARY: {ok}/15 answered | {no_data} no data | {errors} errors\n\n")

        for r in results:
            f.write(f"[{r['num']}/15] {r['category']} — {r['status']}\n")
            f.write(f"Q: {r['question']}\n")
            f.write(f"A: {r['answer']}\n")
            f.write(f"Sources: {', '.join(r['sources']) if r['sources'] else 'none'}\n")
            f.write("-" * 60 + "\n\n")

    print(f"\n{'='*60}")
    print(f"RESULTS: {ok}/15 answered | {no_data} no data | {errors} errors")
    print(f"Full results saved to test_results.txt")
    return results


if __name__ == "__main__":
    run_tests()
