"""
API Testing Script for PaperBuddy

This script helps test each module's endpoint independently.
Run: python test_api.py
"""

import requests
import json

API_BASE_URL = "http://localhost:5175"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")

def test_health():
    """Test health check endpoint"""
    print_section("Testing Health Check")
    response = requests.get(f"{API_BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_info():
    """Test API info endpoint"""
    print_section("Testing API Info")
    response = requests.get(f"{API_BASE_URL}/api/info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_parse_manual():
    """Test Module A - Manual Input Parsing"""
    print_section("Testing Module A: Manual Input Parsing")

    test_data = {
        "title": "Attention Is All You Need",
        "authors": "Vaswani, Ashish, Shazeer, Noam",
        "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.",
        "sections": [
            {
                "heading": "Introduction",
                "content": "Recurrent neural networks have been the dominant approach..."
            },
            {
                "heading": "Model Architecture",
                "content": "Most competitive neural sequence transduction models..."
            }
        ],
        "courseTopic": "NLP"
    }

    response = requests.post(
        f"{API_BASE_URL}/api/parse/manual",
        json=test_data
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_parse_pdf():
    """Test Module A - PDF Parsing"""
    print_section("Testing Module A: PDF Parsing")

    # Note: You need to have a test.pdf file in the same directory
    try:
        with open("test.pdf", "rb") as f:
            files = {"file": f}
            data = {"courseTopic": "CV"}

            response = requests.post(
                f"{API_BASE_URL}/api/parse/pdf",
                files=files,
                data=data
            )

            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
    except FileNotFoundError:
        print("⚠️  test.pdf not found. Skipping PDF test.")
        print("   Create a test.pdf file to test this endpoint.")

def test_summarize():
    """Test Module B - LLM Summarization"""
    print_section("Testing Module B: LLM Summarization")

    paper_data = {
        "title": "Attention Is All You Need",
        "authors": ["Vaswani", "Shazeer"],
        "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and decoder.",
        "sections": [
            {
                "heading": "Introduction",
                "content": "Recurrent models factor computation along positions..."
            }
        ],
        "courseTopic": "NLP"
    }

    response = requests.post(
        f"{API_BASE_URL}/api/summarize",
        json=paper_data
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_generate_images():
    """Test Module C - Image Generation"""
    print_section("Testing Module C: Image Generation")

    image_data = {
        "key_points": [
            "Neural networks learn patterns",
            "Training requires lots of data",
            "Models make predictions"
        ],
        "style": "pastel"
    }

    response = requests.post(
        f"{API_BASE_URL}/api/images/generate",
        json=image_data
    )

    print(f"Status: {response.status_code}")
    result = response.json()

    # Pretty print without full image URLs (they're long)
    if "images" in result:
        print(f"Generated {len(result['images'])} images:")
        for i, img in enumerate(result['images']):
            print(f"  Image {i+1}:")
            print(f"    Key Point: {img.get('key_point')}")
            print(f"    Description: {img.get('description')}")
            print(f"    URL: {img.get('url')[:50]}..." if len(img.get('url', '')) > 50 else img.get('url'))
    else:
        print(f"Response: {json.dumps(result, indent=2)}")

def test_full_pipeline():
    """Test full pipeline integration"""
    print_section("Testing Full Pipeline (Manual Input)")

    # Step 1: Parse manual input
    print("Step 1: Parsing manual input...")
    manual_data = {
        "title": "Test Paper",
        "authors": "Alice, Bob",
        "abstract": "This is a test abstract for pipeline testing.",
        "sections": [],
        "courseTopic": "CV"
    }

    parse_response = requests.post(
        f"{API_BASE_URL}/api/parse/manual",
        json=manual_data
    )

    if parse_response.status_code != 200:
        print(f"❌ Parse failed: {parse_response.json()}")
        return

    paper_data = parse_response.json()
    print("✓ Parse successful")

    # Step 2: Summarize
    print("\nStep 2: Generating summary...")
    summary_response = requests.post(
        f"{API_BASE_URL}/api/summarize",
        json=paper_data
    )

    if summary_response.status_code != 200:
        print(f"❌ Summarize failed: {summary_response.json()}")
        return

    summary = summary_response.json()
    print("✓ Summary generated")

    # Step 3: Generate images
    print("\nStep 3: Generating images...")
    images_response = requests.post(
        f"{API_BASE_URL}/api/images/generate",
        json={
            "key_points": summary.get("steps", ["test point"]),
            "style": "pastel"
        }
    )

    if images_response.status_code != 200:
        print(f"❌ Image generation failed: {images_response.json()}")
        return

    images = images_response.json()
    print("✓ Images generated")

    # Final result
    print("\n" + "-" * 60)
    print("Pipeline completed successfully!")
    print(f"Paper: {paper_data.get('title')}")
    print(f"Big Idea: {summary.get('big_idea')}")
    print(f"Images: {len(images.get('images', []))} generated")
    print("-" * 60)

def main():
    """Run all tests"""
    print("\n" + "🧪" * 30)
    print("PaperBuddy API Testing Suite")
    print("🧪" * 30)

    tests = [
        ("Health Check", test_health),
        ("API Info", test_info),
        ("Module A: Manual Parsing", test_parse_manual),
        ("Module A: PDF Parsing", test_parse_pdf),
        ("Module B: Summarization", test_summarize),
        ("Module C: Image Generation", test_generate_images),
        ("Full Pipeline", test_full_pipeline)
    ]

    print("\nSelect a test to run:")
    print("0. Run all tests")
    for i, (name, _) in enumerate(tests, 1):
        print(f"{i}. {name}")

    choice = input("\nEnter your choice (0-7): ").strip()

    try:
        choice = int(choice)
        if choice == 0:
            # Run all tests
            for name, test_func in tests:
                try:
                    test_func()
                except requests.exceptions.ConnectionError:
                    print(f"❌ Connection failed. Is the server running on {API_BASE_URL}?")
                    break
                except Exception as e:
                    print(f"❌ Test failed: {str(e)}")
        elif 1 <= choice <= len(tests):
            name, test_func = tests[choice - 1]
            try:
                test_func()
            except requests.exceptions.ConnectionError:
                print(f"❌ Connection failed. Is the server running on {API_BASE_URL}?")
            except Exception as e:
                print(f"❌ Test failed: {str(e)}")
        else:
            print("Invalid choice")
    except ValueError:
        print("Invalid input")

    print("\n" + "✅" * 30)
    print("Testing complete!")
    print("✅" * 30 + "\n")

if __name__ == "__main__":
    main()
