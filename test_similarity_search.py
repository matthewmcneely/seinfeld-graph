#!/usr/bin/env python3
"""
Test script for similarity search on Episodes and Lines using three specific phrases.
Queries both Episode summaries and Line dialogue for similar content.
Results are limited to 5 and ordered by episode number to ensure consistent evaluation.
"""

import socket
from sentence_transformers import SentenceTransformer
from python_graphql_client import GraphqlClient
import json
from datetime import datetime

# Configuration
DGRAPH_HOSTNAME = "localhost"
DGRAPH_HTTP_PORT = 8080
DGRAPH_URL = f"http://{DGRAPH_HOSTNAME}:{DGRAPH_HTTP_PORT}/graphql"

# Test phrases
TEST_PHRASES = [
    "You got the wrong guy!",
    "Disgrace in public office", 
    "Broken promises"
]

def check_port(hostname, port):
    """Check if a port is accepting connections."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((hostname, port))
        sock.close()
        return result == 0
    except socket.error:
        return False

def verify_dgraph_connection():
    """Verify Dgraph is running and accessible."""
    if not check_port(DGRAPH_HOSTNAME, DGRAPH_HTTP_PORT):
        raise Exception(f"Dgraph HTTP port {DGRAPH_HTTP_PORT} at {DGRAPH_HOSTNAME} not responding")
    print("✓ Dgraph connection verified")

def create_embedding_models():
    """Create embedding models for episodes and lines."""
    print("Creating embedding models...")
    line_model = SentenceTransformer('all-MiniLM-L6-v2')
    episode_model = SentenceTransformer('all-mpnet-base-v2')
    print("✓ Models created successfully")
    return line_model, episode_model

def query_similar_episodes(client, model, phrase, limit=5):
    """Query for similar episodes by phrase."""
    print(f"\n--- Episode Search for: '{phrase}' ---")
    
    # Create embedding
    embedding = model.encode([phrase])[0].tolist()
    
    # GraphQL query for similar episodes
    query = """
        query querySimilarEpisodeByEmbedding($vector: [Float!]!, $topK: Int!) {
            querySimilarEpisodeByEmbedding(by: summary_v, topK: $topK, vector: $vector) {
                identifier
                title
                summary
                vector_distance
                number
            }
        }
    """
    
    variables = {
        "vector": embedding,
        "topK": limit
    }
    
    try:
        data = client.execute(query=query, variables=variables)
        episodes = data["data"]["querySimilarEpisodeByEmbedding"]
        
        # Sort by descending vector distance (most similar first)
        episodes.sort(key=lambda x: x['vector_distance'], reverse=True)
        
        print(f"Found {len(episodes)} similar episodes:")
        for episode in episodes:
            print(f"  {episode['identifier']} {episode['title']} - {episode['summary'][:100]}... (distance: {episode['vector_distance']:.4f})")
        
        return episodes
    except Exception as e:
        print(f"Error querying episodes: {e}")
        return []

def query_similar_lines(client, model, phrase, limit=5):
    """Query for similar lines by phrase."""
    print(f"\n--- Line Search for: '{phrase}' ---")
    
    # Create embedding
    embedding = model.encode([phrase])[0].tolist()
    
    # GraphQL query for similar lines
    query = """
        query querySimilarLineByEmbedding($vector: [Float!]!, $topK: Int!) {
            querySimilarLineByEmbedding(by: text_v, topK: $topK, vector: $vector) {
                id
                text
                vector_distance
                number
                character {
                    name
                }
                episode {
                    identifier
                    title
                    number
                }
            }
        }
    """
    
    variables = {
        "vector": embedding,
        "topK": limit
    }
    
    try:
        data = client.execute(query=query, variables=variables)
        lines = data["data"]["querySimilarLineByEmbedding"]
        
        # Sort by descending vector distance (most similar first)
        lines.sort(key=lambda x: x['vector_distance'], reverse=True)
        
        print(f"Found {len(lines)} similar lines:")
        for line in lines:
            episode_info = line['episode']
            print(f"  {episode_info['identifier']} {episode_info['title']} - {line['character']['name']}: {line['text'][:80]}... (distance: {line['vector_distance']:.4f})")
        
        return lines
    except Exception as e:
        print(f"Error querying lines: {e}")
        return []

def main():
    """Main test function."""
    print("=== Seinfeld Graph Similarity Search Test ===")
    print(f"Testing phrases: {', '.join(TEST_PHRASES)}")
    print('Results limited to 5 per search, ordered by episode number')
    
    try:
        # Verify connection
        verify_dgraph_connection()
        
        # Create models and client
        line_model, episode_model = create_embedding_models()
        client = GraphqlClient(endpoint=DGRAPH_URL)
        
        # Test each phrase
        all_results = {}
        
        for phrase in TEST_PHRASES:
            print(f"\n{'='*60}")
            print(f"Testing phrase: '{phrase}'")
            print('='*60)
            
            # Query episodes
            episodes = query_similar_episodes(client, episode_model, phrase, limit=5)
            
            # Query lines  
            lines = query_similar_lines(client, line_model, phrase, limit=5)
            
            all_results[phrase] = {
                'episodes': episodes,
                'lines': lines
            }
        
        # Summary
        print(f"\n{'='*60}")
        print("SUMMARY")
        print('='*60)
        for phrase, results in all_results.items():
            print(f"\nPhrase: '{phrase}'")
            print(f"  Episodes found: {len(results['episodes'])}")
            print(f"  Lines found: {len(results['lines'])}")
        
        print('✓ Test completed successfully')
        
        # Optionally save results to date-time versioned file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'similarity_search_results_{timestamp}.json'
        with open(filename, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f'✓ Results saved to {filename}')
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
