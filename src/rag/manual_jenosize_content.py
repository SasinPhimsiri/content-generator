"""Manual Jenosize content examples based on their website style and FUTURE framework."""

from typing import List, Dict, Any
from .simple_vector_store import SimpleVectorStore
from loguru import logger


class ManualJenosizeContent:
    """Manually curated Jenosize-style content based on their FUTURE framework."""
    
    def __init__(self):
        self.vector_store = SimpleVectorStore()
    
    def get_jenosize_examples(self) -> List[Dict[str, Any]]:
        """Get manually created examples based on Jenosize's FUTURE framework and style."""
        
        # Based on https://www.jenosize.com/en/ideas and their FUTURE framework
        examples = [
            {
                "content": """The future of business lies in understanding the convergence of technology and human behavior. As digital transformation accelerates, organizations must adopt a futurist mindset to anticipate market shifts and consumer needs.

Today's successful businesses are those that embrace data-driven insights to understand people and consumer behavior at a deeper level. By leveraging advanced analytics and AI, companies can predict trends, personalize experiences, and create meaningful connections with their audiences.

Transformation and technology go hand in hand. The most effective digital transformations focus not just on implementing new tools, but on reimagining business processes and customer journeys. Organizations that view technology as an enabler rather than an end goal achieve more sustainable results.

Creating utility for our world means developing solutions that genuinely improve people's lives and business outcomes. This requires a holistic approach that considers environmental impact, social responsibility, and long-term value creation.

Real-time marketing has become essential in today's fast-paced digital landscape. Brands must be agile, responsive, and capable of engaging customers across multiple touchpoints simultaneously. Success comes from combining strategic planning with tactical flexibility.

To experience the new world of business, organizations must be willing to experiment, learn, and adapt continuously. The companies that thrive are those that embrace change as an opportunity rather than a threat.""",
                "metadata": {
                    "category": "Digital Transformation",
                    "industry": "General",
                    "tone": "jenosize_professional",
                    "type": "article",
                    "source": "jenosize_style",
                    "framework": "FUTURE",
                    "word_count": 246
                }
            },
            {
                "content": """Understanding people and consumer behavior has never been more critical for business success. In an era where customer expectations evolve rapidly, organizations must develop sophisticated approaches to consumer research and behavioral analysis.

The modern consumer journey is complex, spanning multiple channels and touchpoints. Businesses that excel at mapping these journeys and understanding the emotional drivers behind consumer decisions gain significant competitive advantages. This requires combining quantitative data with qualitative insights to create comprehensive consumer profiles.

Technology enables unprecedented visibility into consumer behavior, but the real value lies in translating these insights into actionable strategies. Organizations must build capabilities in data collection, analysis, and interpretation while maintaining focus on the human elements that drive decision-making.

Successful consumer research goes beyond demographics and purchase history. It explores motivations, aspirations, pain points, and the broader context in which consumers make decisions. This deeper understanding enables businesses to create more relevant products, services, and experiences.

The future belongs to organizations that can seamlessly blend human intuition with data-driven insights. By combining traditional research methods with advanced analytics and AI, businesses can achieve a more complete understanding of their customers and market dynamics.""",
                "metadata": {
                    "category": "Customer Experience",
                    "industry": "General",
                    "tone": "jenosize_professional",
                    "type": "article",
                    "source": "jenosize_style",
                    "framework": "Understand People & Consumer",
                    "word_count": 210
                }
            },
            {
                "content": """Real-time marketing represents a fundamental shift in how businesses engage with their audiences. In today's hyper-connected world, the ability to respond instantly to market changes, consumer behavior, and emerging opportunities can determine competitive success.

The foundation of effective real-time marketing lies in robust data infrastructure and analytics capabilities. Organizations must be able to collect, process, and act on information as it becomes available. This requires investment in technology platforms, data integration, and automated decision-making systems.

However, technology alone is insufficient. Real-time marketing success depends on organizational agility, clear decision-making processes, and empowered teams that can respond quickly to opportunities. Companies must balance automation with human oversight to ensure brand consistency and strategic alignment.

The most effective real-time marketing strategies combine planned content with reactive capabilities. While some campaigns can be automated based on triggers and algorithms, the most impactful moments often require human creativity and strategic thinking.

Measurement and optimization are crucial components of real-time marketing. Organizations must establish metrics that capture both immediate impact and long-term brand value. This includes tracking engagement, conversion, and sentiment across all channels and touchpoints.

Success in real-time marketing requires a cultural shift toward experimentation, learning, and continuous improvement. Organizations that embrace this mindset while maintaining strategic focus achieve the best results.""",
                "metadata": {
                    "category": "AI & Automation",
                    "industry": "General",
                    "tone": "jenosize_professional",
                    "type": "article",
                    "source": "jenosize_style",
                    "framework": "Real-time Marketing",
                    "word_count": 254
                }
            },
            {
                "content": """Digital transformation in retail requires a comprehensive approach that addresses technology, operations, and customer experience simultaneously. The most successful transformations focus on creating seamless omnichannel experiences that meet consumers where they are.

Modern retail success depends on understanding the evolving consumer journey. Today's shoppers expect consistent experiences across online and offline channels, with the ability to research, purchase, and receive support through their preferred touchpoints. Retailers must invest in technology platforms that enable this level of integration.

Data and analytics play a crucial role in retail transformation. By leveraging customer data, inventory information, and market insights, retailers can optimize everything from product assortment to pricing strategies. The key is creating systems that provide actionable insights in real-time.

Personalization has become a competitive necessity rather than a nice-to-have feature. Retailers must develop capabilities to deliver relevant product recommendations, targeted promotions, and customized experiences at scale. This requires sophisticated data management and AI-powered recommendation engines.

The future of retail lies in creating experiences that blend digital convenience with human connection. Successful retailers understand that technology should enhance rather than replace human interaction, creating opportunities for meaningful engagement throughout the customer journey.

Sustainability and social responsibility are increasingly important factors in retail transformation. Consumers expect brands to demonstrate genuine commitment to environmental and social causes, requiring retailers to integrate these values into their operations and communications.""",
                "metadata": {
                    "category": "Digital Transformation",
                    "industry": "Retail & E-commerce",
                    "tone": "jenosize_professional",
                    "type": "article",
                    "source": "jenosize_style",
                    "framework": "Experience the New World",
                    "word_count": 268
                }
            },
            {
                "content": """The financial services industry stands at the intersection of regulatory requirements and digital innovation. Banks and insurance companies must navigate complex compliance landscapes while delivering the modern experiences that customers expect.

Digital transformation in financial services requires careful balance between innovation and risk management. Organizations must implement new technologies and processes while maintaining the security, reliability, and regulatory compliance that are fundamental to financial operations.

Customer expectations in financial services have evolved dramatically. Consumers now expect the same level of convenience and personalization they receive from other digital services. This includes mobile-first experiences, instant transactions, and proactive financial guidance.

Artificial intelligence and machine learning are transforming financial services operations. From fraud detection to credit scoring, AI enables more accurate risk assessment and improved customer service. However, implementation must consider regulatory requirements and ethical implications.

The future of financial services lies in creating utility for customers' financial lives. This means moving beyond traditional banking products to provide comprehensive financial wellness solutions. Successful organizations will be those that help customers achieve their financial goals through technology-enabled services.

Open banking and API-first architectures are enabling new forms of collaboration and innovation. Financial institutions must develop platform strategies that allow them to participate in broader financial ecosystems while maintaining competitive differentiation.""",
                "metadata": {
                    "category": "Digital Transformation",
                    "industry": "Financial Services",
                    "tone": "jenosize_professional",
                    "type": "article",
                    "source": "jenosize_style",
                    "framework": "Utility for Our World",
                    "word_count": 238
                }
            }
        ]
        
        return examples
    
    def add_to_vector_store(self) -> int:
        """Add Jenosize-style examples to the vector store."""
        examples = self.get_jenosize_examples()
        added_count = 0
        
        for i, example in enumerate(examples):
            try:
                doc_id = f"jenosize_manual_{i+1}"
                
                self.vector_store.add_document(
                    content=example["content"],
                    metadata=example["metadata"],
                    doc_id=doc_id
                )
                
                added_count += 1
                framework = example["metadata"].get("framework", "N/A")
                logger.info(f"Added Jenosize example: {framework}")
                
            except Exception as e:
                logger.warning(f"Failed to add example {i+1}: {e}")
        
        return added_count


def update_with_manual_content():
    """Update the vector store with manually created Jenosize content."""
    logger.info("Adding manual Jenosize-style content...")
    
    content_manager = ManualJenosizeContent()
    added_count = content_manager.add_to_vector_store()
    
    logger.info(f"Successfully added {added_count} Jenosize-style examples")
    return added_count


if __name__ == "__main__":
    count = update_with_manual_content()
    print(f"Added {count} Jenosize-style examples to the vector store")
