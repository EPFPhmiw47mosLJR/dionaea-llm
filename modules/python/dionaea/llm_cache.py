# This file is part of the dionaea honeypot
#
# SPDX-FileCopyrightText: 2025
# SPDX-License-Identifier: GPL-2.0-or-later

"""
LLM Cache Service Client for Dionaea

This module provides a client to communicate with an LLM cache service
that simulates execution responses for HTTP requests.
"""

import json
import logging
import os
import urllib.request
import urllib.error
from typing import Optional

logger = logging.getLogger('llm_cache')
logger.setLevel(logging.DEBUG)


class LLMCacheClient:
    """
    Client for communicating with the LLM cache service.
    Reads configuration from environment variables:
    - LLM_CACHE_URL: The base URL of the LLM cache service
    - LLM_CACHE_PORT: The port of the LLM cache service
    - LLM_CACHE_ENDPOINT: The endpoint path for queries
    """

    def __init__(self):
        self.url = os.environ.get("LLM_CACHE_URL", "http://localhost")
        self.port = os.environ.get("LLM_CACHE_PORT", "8080")
        self.endpoint = os.environ.get("LLM_CACHE_ENDPOINT", "/query")
        
        # Build the full URL
        self.full_url = f"{self.url}:{self.port}{self.endpoint}"
        
        # Check if LLM cache is enabled
        self.enabled = all([
            os.environ.get("LLM_CACHE_URL"),
            os.environ.get("LLM_CACHE_PORT"),
            os.environ.get("LLM_CACHE_ENDPOINT")
        ])
        
        if self.enabled:
            logger.info(f"LLM Cache client initialized: {self.full_url}")
        else:
            logger.info("LLM Cache client disabled (environment variables not set)")

    def query_request(self, request_content: str, timeout: int = 5) -> Optional[str]:
        """
        Query the LLM cache service with a request.
        
        Args:
            request_content: The request content to query (e.g., URL path, command)
            timeout: Timeout in seconds for the HTTP request
            
        Returns:
            The response string from the LLM cache, or None if the query fails
        """
        if not self.enabled:
            return None
            
        try:
            # Prepare the JSON payload
            payload = {"content": request_content}
            json_data = json.dumps(payload).encode("utf-8")
            
            # Create the HTTP request
            req = urllib.request.Request(
                self.full_url,
                data=json_data,
                headers={
                    "Content-Type": "application/json",
                    "Content-Length": str(len(json_data))
                },
                method="POST"
            )
            
            logger.debug(f"Querying LLM cache for request: {request_content}")
            
            # Make the POST request
            with urllib.request.urlopen(req, timeout=timeout) as response:
                body = response.read()
            
            # Parse the JSON response
            response_data = json.loads(body.decode("utf-8"))
            llm_response = response_data.get("response", "")
            
            logger.debug(f"LLM cache response received for: {request_content}")
            return llm_response
            
        except urllib.error.URLError as e:
            logger.error(f"Error querying LLM cache (URLError): {e}")
            return None
        except urllib.error.HTTPError as e:
            logger.error(f"Error querying LLM cache (HTTPError): {e.code} {e.reason}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing LLM cache response: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error querying LLM cache: {e}")
            return None


# Global singleton instance
_llm_cache_client = None


def get_llm_cache_client() -> LLMCacheClient:
    """
    Get the global LLM cache client instance (singleton pattern)
    """
    global _llm_cache_client
    if _llm_cache_client is None:
        _llm_cache_client = LLMCacheClient()
    return _llm_cache_client
