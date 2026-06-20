import React, { useState } from 'react';

const CaveatBadge = ({ caveats }) => {
  if (!caveats || caveats.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
      <div className="flex gap-2">
        <span className="text-lg">⚠</span>
        <div>
          <p className="font-semibold text-yellow-900 text-sm">Data gaps:</p>
          <p className="text-yellow-800 text-sm mt-1">
            {caveats.join(', ')}
          </p>
        </div>
      </div>
    </div>
  );
};

export default CaveatBadge;
