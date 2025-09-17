import logging
from typing import Optional, Dict, Any
from decouple import config
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class AIStoryGenerator:
    """
    AI-powered story generator using Google Gemini API
    """
    
    def __init__(self):
        self.api_key = config('GEMINI_API_KEY', default=None)
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Gemini client if API key is available"""
        if self.api_key and self.api_key != 'your-gemini-api-key-here':
            try:
                # Initialize client with explicit API key
                import os
                os.environ['GEMINI_API_KEY'] = self.api_key
                self.client = genai.Client(api_key=self.api_key)
                logger.info("Gemini AI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.client = None
        else:
            logger.warning("Gemini API key not configured, falling back to simple generation")
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.client is not None
    
    def generate_story(self, keywords: str, genre: str, length: str, tone: str) -> Dict[str, Any]:
        """
        Generate a story using AI or fallback to simple generation
        
        Args:
            keywords: User-provided keywords for the story
            genre: Story genre (fantasy, sci_fi, etc.)
            length: Story length (short, medium, long)
            tone: Story tone (happy, dark, etc.)
            
        Returns:
            Dict containing story content and metadata
        """
        if self.is_available():
            return self._generate_with_ai(keywords, genre, length, tone)
        else:
            return self._generate_simple(keywords, genre, length, tone)
    
    def _generate_with_ai(self, keywords: str, genre: str, length: str, tone: str) -> Dict[str, Any]:
        """Generate story using Gemini AI"""
        try:
            # Create a detailed prompt for better story generation
            prompt = self._create_prompt(keywords, genre, length, tone)
            
            # Configure the generation with thinking disabled for faster response
            config_obj = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            )
            
            # Make the API call
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=config_obj
            )
            
            if response and response.text:
                return {
                    'content': response.text.strip(),
                    'ai_model_used': 'gemini-2.5-flash',
                    'generation_method': 'ai'
                }
            else:
                logger.warning("Empty response from Gemini API, falling back to simple generation")
                return self._generate_simple(keywords, genre, length, tone)
                
        except Exception as e:
            logger.error(f"Error generating story with AI: {e}")
            # Fallback to simple generation
            return self._generate_simple(keywords, genre, length, tone)
    
    def _create_prompt(self, keywords: str, genre: str, length: str, tone: str) -> str:
        """Create a detailed prompt for the AI"""
        
        # Map length to approximate word counts
        length_mapping = {
            'short': '100-300 words',
            'medium': '300-600 words', 
            'long': '600-1000 words'
        }
        
        # Map genre to descriptions
        genre_descriptions = {
            'fantasy': 'a magical fantasy world with mythical creatures, magic, and adventure',
            'sci_fi': 'a futuristic science fiction setting with advanced technology, space, or aliens',
            'romance': 'a romantic story focusing on love, relationships, and emotional connections',
            'horror': 'a suspenseful horror story with dark, scary, or supernatural elements',
            'mystery': 'a mysterious detective or puzzle story with secrets to uncover',
            'adventure': 'an exciting adventure story with action, exploration, and challenges',
            'drama': 'a dramatic story with deep emotions, conflict, and character development',
            'comedy': 'a humorous and lighthearted story with funny situations and characters'
        }
        
        # Map tone to descriptions
        tone_descriptions = {
            'happy': 'upbeat, positive, and cheerful',
            'dark': 'serious, somber, and intense',
            'humorous': 'funny, witty, and entertaining',
            'dramatic': 'emotional, intense, and compelling',
            'mysterious': 'enigmatic, suspenseful, and intriguing',
            'romantic': 'loving, passionate, and heartfelt'
        }
        
        word_count = length_mapping.get(length, '100-300 words')
        genre_desc = genre_descriptions.get(genre, 'an engaging fictional story')
        tone_desc = tone_descriptions.get(tone, 'engaging')
        
        prompt = f"""Write a complete, well-structured story of {word_count} set in {genre_desc}. 
The story should have a {tone_desc} tone and must incorporate these keywords naturally: {keywords}

Requirements:
- Create a compelling narrative with a clear beginning, middle, and end
- Develop interesting characters and vivid descriptions
- Ensure the keywords "{keywords}" are woven naturally into the plot
- Match the {genre} genre and {tone} tone throughout
- Write approximately {word_count}
- Use engaging prose that draws the reader in
- Include dialogue if appropriate to the story

Please write only the story content, without any meta-commentary or explanations."""
        
        return prompt
    
    def _generate_simple(self, keywords: str, genre: str, length: str, tone: str) -> Dict[str, Any]:
        """
        Fallback simple story generation (original algorithm)
        This is used when AI is not available
        """
        import random
        
        # Story templates based on genre (from original implementation)
        templates = {
            'fantasy': [
                "In a realm where magic flows like rivers, {keywords} discovered an ancient secret that would change everything.",
                "The wizard gazed upon {keywords}, knowing that destiny had finally arrived at their doorstep.",
                "Deep in the enchanted forest, {keywords} awakened powers beyond imagination."
            ],
            'sci_fi': [
                "In the year 2157, {keywords} became humanity's last hope against the alien invasion.",
                "The space station orbited silently as {keywords} made a discovery that defied all known physics.",
                "Through the quantum portal, {keywords} glimpsed a future that both terrified and amazed them."
            ],
            'romance': [
                "Their eyes met across the crowded room, and {keywords} knew this moment would change everything.",
                "Love bloomed unexpectedly when {keywords} entered their life like spring after endless winter.",
                "The letter spoke of {keywords}, and suddenly the heart understood what it had been searching for."
            ],
            'horror': [
                "The darkness whispered of {keywords}, and terror crept through every shadow of the old house.",
                "They should never have disturbed {keywords}, for some secrets are buried for good reason.",
                "The mirror reflected not their face, but {keywords} staring back with hollow, hungry eyes."
            ],
            'mystery': [
                "The detective examined {keywords}, knowing this clue would either solve the case or lead to more questions.",
                "Nobody could explain how {keywords} appeared in the locked room, but Detective Morgan was determined to find out.",
                "The ancient diary mentioned {keywords} three times, always on the nights when people disappeared."
            ]
        }
        
        # Get random template
        genre_templates = templates.get(genre, templates['fantasy'])
        template = random.choice(genre_templates)
        
        # Generate story content
        story_start = template.format(keywords=keywords)
        
        # Add middle and ending based on length
        word_targets = {'short': 150, 'medium': 400, 'long': 700}
        target_words = word_targets.get(length, 150)
        
        # Simple continuation
        middle_parts = [
            f"The journey began with uncertainty, but {keywords} provided the guidance needed.",
            f"Challenges arose that tested every belief about {keywords} and its true meaning.",
            f"As time passed, the significance of {keywords} became increasingly clear.",
            f"Others had searched for {keywords} before, but none had come this close to the truth."
        ]
        
        ending_parts = {
            'happy': f"In the end, {keywords} brought joy and fulfillment beyond all expectations.",
            'dark': f"The truth about {keywords} was darker than anyone could have imagined.",
            'humorous': f"Who would have thought that {keywords} could lead to such amusing adventures?",
            'dramatic': f"The final revelation about {keywords} changed everything they thought they knew.",
            'mysterious': f"Even now, the true nature of {keywords} remains shrouded in mystery.",
            'romantic': f"Love conquered all, and {keywords} became the symbol of their eternal bond."
        }
        
        # Build full story
        story_parts = [story_start]
        
        # Add middle parts based on target length
        num_middle = min(len(middle_parts), max(1, target_words // 50))
        story_parts.extend(random.sample(middle_parts, num_middle))
        
        # Add ending
        ending = ending_parts.get(tone, ending_parts['dramatic'])
        story_parts.append(ending)
        
        return {
            'content': " ".join(story_parts),
            'ai_model_used': 'simple_algorithm',
            'generation_method': 'template'
        }

# Global instance for easy importing
ai_story_generator = AIStoryGenerator() 