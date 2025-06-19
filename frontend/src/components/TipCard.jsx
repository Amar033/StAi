import React from "react";

const TipCard = ({ icon: Icon, title, content, theme = "primary" }) => {
  const themeColors = {
    primary: "border-primary-500 bg-background-800 text-text-100",
    accent: "border-accent-500 bg-background-800 text-text-100",
    secondary: "border-secondary-500 bg-background-800 text-text-100",
  };

  return (
    <div className={`rounded-xl border-2 p-5 flex flex-col items-center text-center shadow-md transition-all duration-300 ${themeColors[theme]}`}>
      {Icon && <Icon className={`w-10 h-10 mb-3 text-${theme}-400`} />}
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-sm text-text-400">{content}</p>
    </div>
  );
};

export default TipCard;
