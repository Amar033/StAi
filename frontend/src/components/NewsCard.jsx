import { ExternalLink } from "lucide-react";
import React from "react";

const glowClasses = {
  positive: "border-green-500 shadow-[0_0_10px_#22c55e30]",
  neutral: "border-yellow-400 shadow-[0_0_10px_#facc1530]",
  negative: "border-red-500 shadow-[0_0_10px_#ef444430]",
};

const sentimentText = {
  positive: "Positive",
  neutral: "Neutral",
  negative: "Negative",
};

const NewsCard = ({ article }) => {
  const sentiment = article.sentiment.toLowerCase();

  return (
    <a
      href={article.url}
      target="_blank"
      rel="noopener noreferrer"
      className={`block p-4 rounded-xl bg-background-800/60 border border-background-600/30 hover:scale-[1.015] hover:border-primary-500 transition-transform duration-300 ease-out ${glowClasses[sentiment]}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-text-100 mb-1">{article.title}</h3>
          <p className="text-sm text-text-500 mb-2">{article.source}</p>
        </div>
        <ExternalLink className="w-5 h-5 text-text-400 mt-1" />
      </div>
      <span
        className={`text-xs px-2 py-1 rounded-full font-medium bg-background-700 text-${sentiment}-400 border border-${sentiment}-400`}
      >
        {sentimentText[sentiment]}
      </span>
    </a>
  );
};

export default NewsCard;
