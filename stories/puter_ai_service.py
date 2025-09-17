import logging
import random
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PuterAIStoryGenerator:
    """
    AI-powered story generator using Puter.js Claude API - No API keys required!
    """
    
    def __init__(self):
        # Puter.js doesn't need API keys - it's always available
        self.client_available = True
        logger.info("Puter.js Claude AI service initialized - no API key required!")
    
    def is_available(self) -> bool:
        """Check if AI service is available - Puter.js is always available"""
        return self.client_available
    
    def generate_story(self, keywords: str, genre: str, length: str, tone: str) -> Dict[str, Any]:
        """
        Generate a story using Puter.js Claude AI or fallback to simple generation
        
        Args:
            keywords: User-provided keywords for the story
            genre: Story genre (fantasy, sci_fi, etc.)
            length: Story length (short, medium, long)
            tone: Story tone (happy, dark, etc.)
            
        Returns:
            Dict containing story content and metadata
        """
        try:
            if self.is_available():
                return self._generate_with_claude(keywords, genre, length, tone)
            else:
                return self._generate_simple(keywords, genre, length, tone)
        except Exception as e:
            logger.error(f"Story generation failed: {e}")
            return self._generate_simple(keywords, genre, length, tone)
    
    def _generate_with_claude(self, keywords: str, genre: str, length: str, tone: str) -> Dict[str, Any]:
        """Generate story using Puter.js Claude AI - will be handled by frontend"""
        try:
            # Create the prompt for Claude
            prompt = self._create_prompt(keywords, genre, length, tone)
            
            # Return a special marker that the frontend will detect and replace with Claude generation
            logger.info("Preparing Claude AI generation via Puter.js")
            return {
                'content': f"PUTER_CLAUDE_GENERATION||{prompt}",
                'ai_model_used': 'claude-sonnet-4',
                'generation_method': 'ai',
                'prompt': prompt
            }
                
        except Exception as e:
            logger.error(f"Claude AI generation preparation failed: {e}")
            return self._generate_simple(keywords, genre, length, tone)
    
    def _create_prompt(self, keywords: str, genre: str, length: str, tone: str) -> str:
        """Create a detailed prompt for Claude AI story generation"""
        
        # Map length to word counts
        length_mapping = {
            'short': '100-300 words',
            'medium': '300-600 words', 
            'long': '600-1000 words'
        }
        
        word_count = length_mapping.get(length, '300-600 words')
        
        prompt = f"""Write a creative {genre} story with a {tone} tone, approximately {word_count}.

Key elements to include:
- Keywords/themes: {keywords}
- Genre: {genre.replace('_', ' ').title()}
- Tone: {tone.title()}
- Length: {word_count}

Requirements:
- Create engaging characters and dialogue
- Include vivid descriptions and settings
- Build towards a satisfying conclusion
- Make the story interesting and entertaining
- Incorporate all the provided keywords naturally
- Match the requested tone throughout

Please write only the story content, no additional commentary or explanations."""

        return prompt
    
    def _generate_simple(self, keywords: str, genre: str, length: str, tone: str) -> Dict[str, Any]:
        """Fallback method using template-based generation"""
        logger.info("Using template-based story generation as fallback")
        
        # Split keywords into individual words
        keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
        
        # Enhanced genre-specific templates
        templates = {
            'fantasy': [
                "In a realm where magic flows like rivers, {hero} discovered {item}. The {tone_adj} prophecy spoke of {keyword1}, leading to an epic quest through {location}. As {keyword2} appeared, the destiny of all magical beings hung in the balance.",
                "Deep in the enchanted forest, {hero} awakened powers beyond imagination. {keyword1} whispered ancient secrets while {keyword2} illuminated the path. The {tone_adj} journey would test every magical ability.",
                "The crystal tower stood tall against the crimson sky. {hero} wielded {item} with {tone_adj} determination. {keyword1} and {keyword2} were the keys to unlocking the ancient magic that could save their world."
            ],
            'sci_fi': [
                "In the year 2087, {hero} piloted through the cosmic void where {keyword1} held the secrets of faster-than-light travel. The {tone_adj} discovery of {keyword2} would revolutionize space exploration forever.",
                "The space station orbited a dying star when {hero} detected unusual signals from {keyword1}. With {tone_adj} precision, they analyzed how {keyword2} could reshape humanity's understanding of the universe.",
                "On the frontier planet, {hero} engineered a solution involving {keyword1}. The {tone_adj} consequences of combining {keyword2} with alien technology would echo across the galaxy."
            ],
            'mystery': [
                "Detective {hero} examined the crime scene where {keyword1} provided the only clue. The {tone_adj} investigation led through shadows where {keyword2} revealed shocking truths about the case.",
                "The old mansion held secrets that {hero} was determined to uncover. {keyword1} appeared in every room, while {keyword2} whispered of {tone_adj} revelations that would solve the decades-old mystery.",
                "In the foggy streets, {hero} followed a trail of {keyword1}. The {tone_adj} pursuit of {keyword2} led to a confrontation that would expose the truth behind the conspiracy."
            ],
            'romance': [
                "When {hero} met their soulmate at the {keyword1} festival, {keyword2} became their shared passion. Their {tone_adj} love story unfolded like a beautiful dream come true.",
                "The coffee shop where {hero} worked became magical when {keyword1} brought two hearts together. With {keyword2} as their witness, they discovered a {tone_adj} love that transcended time.",
                "Under the starlit sky, {hero} realized that {keyword1} was just the beginning. {keyword2} symbolized their {tone_adj} commitment to a future filled with endless possibilities."
            ],
            'horror': [
                "The abandoned house echoed with whispers when {hero} discovered {keyword1} in the basement. The {tone_adj} presence of {keyword2} awakened something that should have stayed buried.",
                "Midnight struck as {hero} realized {keyword1} was more than just coincidence. The {tone_adj} manifestation of {keyword2} brought forth terrors from beyond the veil.",
                "In the storm-lashed cemetery, {hero} uncovered the truth about {keyword1}. The {tone_adj} curse connected to {keyword2} would haunt their nightmares forever."
            ],
            'adventure': [
                "The treasure map led {hero} through treacherous jungles where {keyword1} marked the path. With {tone_adj} courage, they used {keyword2} to overcome deadly obstacles.",
                "High in the mountain peaks, {hero} discovered that {keyword1} was the key to the ancient temple. The {tone_adj} challenge of {keyword2} tested every survival skill.",
                "The pirate ship sailed into uncharted waters where {hero} sought {keyword1}. With {keyword2} as their guide, they embarked on a {tone_adj} expedition that would change everything."
            ]
        }
        
        # Get templates for the genre or default to adventure
        genre_templates = templates.get(genre, templates['adventure'])
        
        # Choose a random template
        template = random.choice(genre_templates)
        
        # Generate random elements
        heroes = ["Alex", "Maya", "Jordan", "Riley", "Casey", "Morgan", "Avery", "Quinn"]
        items = ["mystical artifact", "ancient scroll", "glowing crystal", "enchanted weapon", "magical pendant"]
        locations = ["hidden valleys", "mysterious caves", "floating islands", "underground cities", "twilight realms"]
        
        # Map tones to adjectives
        tone_adjectives = {
            'happy': 'joyful',
            'sad': 'melancholic', 
            'mysterious': 'enigmatic',
            'exciting': 'thrilling',
            'dark': 'ominous',
            'funny': 'humorous',
            'romantic': 'passionate',
            'epic': 'heroic'
        }
        
        # Fill in the template
        story = template.format(
            hero=random.choice(heroes),
            item=random.choice(items),
            location=random.choice(locations),
            keyword1=keyword_list[0] if keyword_list else "destiny",
            keyword2=keyword_list[1] if len(keyword_list) > 1 else "adventure",
            tone_adj=tone_adjectives.get(tone, 'remarkable')
        )
        
        # Add conclusion based on length
        length_multipliers = {'short': 1, 'medium': 2, 'long': 3}
        multiplier = length_multipliers.get(length, 1)
        
        if multiplier > 1:
            # Add more content for medium/long stories
            additional_content = [
                f" The journey continued as unexpected challenges involving {keyword_list[0] if keyword_list else 'mystery'} tested their resolve.",
                f" With each step forward, the connection to {keyword_list[1] if len(keyword_list) > 1 else 'their goal'} grew stronger.",
                f" As the final chapter of this {tone} tale unfolded, everything led to a {tone_adjectives.get(tone, 'remarkable')} conclusion."
            ]
            
            for i in range(min(multiplier - 1, len(additional_content))):
                story += additional_content[i]
        
        return {
            'content': story,
            'ai_model_used': 'template-based',
            'generation_method': 'template'
        }

# Create a global instance to use throughout the app
puter_ai_generator = PuterAIStoryGenerator() 